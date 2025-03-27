import folium
from streamlit_folium import st_folium
import pandas as pd
from pathlib import Path
from geopy.distance import geodesic
import streamlit as st  # Added this import


# Load airport data from CSV
def load_airport_data():
    try:
        csv_path = Path(__file__).parent / 'airport_data.csv'  # Adjust path as needed
        df = pd.read_csv(csv_path)
        # Fixed the column selection syntax
        return df.set_index('iata_code')[['latitude_deg', 'longitude_deg']].to_dict('index')
    except Exception as e:
        print(f"Failed to load airport data: {str(e)}")  # Changed from st.error to print
        return {}


# Preload airport coordinates
AIRPORT_COORDS = load_airport_data()


def get_coordinates(location):
    """
    Get coordinates for a location (can be city name or airport code)
    Returns (lat, lon) or None if not found
    """
    # First try as airport code
    if location.upper() in AIRPORT_COORDS:
        coords = AIRPORT_COORDS[location.upper()]
        return (coords['latitude_deg'], coords['longitude_deg'])

    # If not found, implement city name lookup here if needed
    # You could add a city-to-airport mapping dictionary
    return None


def show_map(source, destination):
    """
    Create and display a folium map between two locations
    Args:
        source: Source location (city name or airport code)
        destination: Destination location (city name or airport code)
    """
    # Get coordinates
    source_coords = get_coordinates(source)
    dest_coords = get_coordinates(destination)

    if not source_coords or not dest_coords:
        return None, "Could not find coordinates for one or both locations"

    # Calculate midpoint for centering
    midpoint = [(source_coords[0] + dest_coords[0]) / 2,
                (source_coords[1] + dest_coords[1]) / 2]

    # Create map
    travel_map = folium.Map(location=midpoint, zoom_start=6)

    # Add markers
    folium.Marker(
        location=source_coords,
        popup=f"Departure: {source}",
        icon=folium.Icon(color="green", icon="plane", prefix="fa")
    ).add_to(travel_map)

    folium.Marker(
        location=dest_coords,
        popup=f"Destination: {destination}",
        icon=folium.Icon(color="red", icon="hotel", prefix="fa")
    ).add_to(travel_map)

    # Add route line
    folium.PolyLine(
        locations=[source_coords, dest_coords],
        color="blue",
        weight=2.5,
        opacity=1,
        dash_array='5,5'
    ).add_to(travel_map)

    # Calculate distance
    distance_km = geodesic(source_coords, dest_coords).km

    return travel_map, distance_km


def display_map_in_chat(source, destination):
    """
    Display map directly in Streamlit chat
    """
    map_obj, distance = show_map(source, destination)

    if map_obj is None:
        st.error(distance)  # Now we can use st.error here
        return

    with st.chat_message("assistant"):
        st.write(f"### Route from {source.upper()} to {destination.upper()}")
        st_folium(map_obj, width=700, height=400)
        st.write(f"**Approximate distance:** {distance:.0f} km")
        st.write("*Note: Route shows straight-line distance between airports*")