import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

class HotelScraper:
    def __init__(self):
        # Load airport mapping from JSON file
        try:
            with open(Path(__file__).parent / 'airport_mapping.json', 'r') as f:
                self.airport_mapping = json.load(f)
        except FileNotFoundError:
            raise Exception("airport_mapping.json file not found")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON in airport_mapping.json")

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        }
        self.base_url = "https://www.booking.com"

    def search_hotels(self, destination, check_in, nights, budget=None, min_rating=None):
        try:
            # Find the destination in our airport mapping
            normalized_dest = destination.lower().strip()
            if normalized_dest not in self.airport_mapping:
                # Try to find a matching city name in the airport mapping
                matching_cities = [city for city in self.airport_mapping.keys()
                                 if normalized_dest in city.lower()]
                if not matching_cities:
                    return {"error": f"Could not find destination {destination} in our database"}

                # Use the first matching city
                normalized_dest = matching_cities[0].lower()

            # Get the airport name for the destination
            airport_name = self.airport_mapping[normalized_dest]["name"]
            city_name = airport_name.split(" Airport")[0].split(" International")[0].strip()

            # Calculate check-out date (fixed syntax error here)
            check_out = (datetime.strptime(check_in, "%Y-%m-%d") +
                        timedelta(days=nights)).strftime("%Y-%m-%d")

            # Build search URL
            search_url = f"{self.base_url}/searchresults.en-gb.html"
            params = {
                "ss": city_name,
                "checkin": check_in,
                "checkout": check_out,  # Fixed variable name (was check_out_str)
                "group_adults": "2",
                "group_children": "0",
                "no_rooms": "1",
                "order": "popularity",
                "nflt": f"review_score={min_rating*20 if min_rating else ''}"
            }

            if budget:
                params["nflt"] += f";price={budget}-{budget*2}"


            # Make the search request
            resp = requests.get(search_url, headers=self.headers, params=params)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Scrape hotel listings
            hotels = []
            listings = soup.find_all("div", {"data-testid": "property-card"})[:5]  # Get top 5 hotels

            for listing in listings:
                try:
                    hotel = {}

                    # Name and link
                    name_elem = listing.find("div", {"data-testid": "title"})
                    hotel["name"] = name_elem.text.strip()
                    hotel["link"] = self.base_url + name_elem.parent["href"]

                    # Address
                    address_elem = listing.find("span", {"data-testid": "address"})
                    hotel["address"] = address_elem.text.strip() if address_elem else "Address not available"

                    # Rating
                    rating_elem = listing.find("div", {"class": "b5cd09854e d10a6220b4"})
                    hotel["rating"] = rating_elem.text.strip() if rating_elem else "No rating"

                    # Price
                    price_elem = listing.find("span", {"data-testid": "price-and-discounted-price"})
                    hotel["price"] = price_elem.text.strip() if price_elem else "Price not available"

                    # Photo
                    photo_elem = listing.find("img", {"data-testid": "image"})
                    hotel["photo"] = photo_elem[
                        "src"] if photo_elem else "https://via.placeholder.com/300x200?text=No+Image"

                    hotels.append(hotel)

                except Exception as e:
                    print(f"Error parsing hotel listing: {e}")
                    continue

            return {
                "hotels": hotels,
                "search_params": {
                    "destination": city_name,
                    "check_in": datetime.strptime(check_in, "%Y-%m-%d").strftime('%b %d, %Y'),
                    "nights": nights,
                    "max_price": f"₹{budget}" if budget else "Not specified",
                    "min_rating": f"{min_rating}⭐" if min_rating else "Not specified"
                }
            }

        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    def get_hotel_details(self, hotel_url):
        """Get detailed information for a specific hotel"""
        try:
            resp = requests.get(hotel_url, headers=self.headers)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            details = {}

            # Hotel name
            name_elem = soup.find("h2", {"class": "pp-header__title"})
            details["name"] = name_elem.text.strip() if name_elem else "Unknown"

            # Address
            address_elem = soup.find("span", {"class": "hp_address_subtitle"})
            details["address"] = address_elem.text.strip() if address_elem else "Address not available"

            # Rating
            rating_elem = soup.find("div", {"class": "b5cd09854e d10a6220b4"})
            details["rating"] = rating_elem.text.strip() if rating_elem else "No rating"

            # Facilities
            facilities = []
            facility_elems = soup.find_all("div", {"class": "important_facility"})
            for elem in facility_elems:
                facilities.append(elem.text.strip("\n").strip())
            details["facilities"] = facilities

            # Room types and prices
            rooms = []
            room_rows = soup.find_all("tr", {"class": "hprt-table-row"})

            for row in room_rows:
                try:
                    room = {}

                    # Room type
                    room_type_elem = row.find("span", {"class": "hprt-roomtype-icon-link"})
                    room["type"] = room_type_elem.text.strip() if room_type_elem else "Unknown room type"

                    # Price
                    price_elem = row.find("div", {"class": "bui-price-display__value"})
                    room["price"] = price_elem.text.strip() if price_elem else "Price not available"

                    rooms.append(room)
                except:
                    continue

            details["rooms"] = rooms

            return details

        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}