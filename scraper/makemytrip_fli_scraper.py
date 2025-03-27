import json
import os
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent


class FlightScraper:
    def __init__(self):
        # Initialize airport mapping
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "airport_mapping.json")
        with open(json_path, "r") as file:
            self.airport_data = json.load(file)

        # Create lookup dictionaries
        self.iata_mapping = {data['iata']: city.lower() for city, data in self.airport_data.items()}
        self.city_mapping = {city.lower(): data['iata'] for city, data in self.airport_data.items()}

        # Initialize user agent
        self.ua = UserAgent()

    def resolve_iata(self, location_name):
        """Resolve location name to IATA code"""
        location_name = location_name.lower().strip()

        if location_name in self.city_mapping:
            return self.city_mapping[location_name]
        if location_name.upper() in self.iata_mapping:
            return location_name.upper()
        for city in self.city_mapping:
            if location_name in city:
                return self.city_mapping[city]
        return None

    def get_flight_data(self, source, destination, date):
        """Get flight data from Google Flights"""
        try:
            source_iata = self.resolve_iata(source)
            dest_iata = self.resolve_iata(destination)

            if not source_iata or not dest_iata:
                return {"error": "Invalid source or destination"}

            formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
            url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest_iata}%20from%20{source_iata}%20on%20{formatted_date}&curr=INR"

            headers = {
                'User-Agent': self.ua.random,
                'Accept-Language': 'en-US,en;q=0.9',
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try multiple selectors for flight listings
            listings = (soup.select('li.pIav2d') or
                        soup.select('div.yR1fYc') or
                        soup.select('div[role="listitem"]'))

            if not listings:
                return {"error": "No flights found or couldn't parse the page"}

            flights = []
            for listing in listings[:5]:  # Limit to 5 results
                try:
                    # Extract and clean data with fallbacks
                    airline = listing.select_one('div.Ir0Voe, div[aria-label*="Airline"]')
                    airline = airline.get_text(' ', strip=True) if airline else "Unknown Airline"
                    airline = ' '.join(airline.split()).replace('-', '').strip()

                    price = listing.select_one('div.YMlIz, span[aria-label*="Price"]')
                    price = price.get_text(' ', strip=True) if price else "Price N/A"
                    price = f"₹{price.replace('₹', '').strip()}"

                    duration = listing.select_one('div.gvkrdb, div[aria-label*="Duration"]')
                    duration = duration.get_text(' ', strip=True) if duration else "Duration N/A"

                    stops = listing.select_one('div.EfT7Ae, div[aria-label*="Stop"]')
                    stops = stops.get_text(' ', strip=True) if stops else "Stops N/A"

                    flights.append({
                        "airline": airline,
                        "price": price,
                        "duration": duration,
                        "stops": stops,
                        "booking_url": url
                    })
                except Exception as e:
                    continue

            return {
                "flights": flights,
                "search_url": url,
                "source": "google_flights"
            } if flights else {"error": "Could not extract flight information"}

        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}