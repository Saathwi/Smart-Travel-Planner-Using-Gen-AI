# utils/map_utils.py
import folium
from streamlit_folium import st_folium
import streamlit as st
from geopy.geocoders import Nominatim
import time


def get_coordinates(location_name):
    """Get latitude and longitude for a location name."""
    geolocator = Nominatim(user_agent="travel_planner")
    try:
        location = geolocator.geocode(location_name)
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception as e:
        st.error(f"Geocoding error: {str(e)}")
        return None


def show_map(location=None, zoom_start=12):
    """Show a map centered at the given location."""
    if location:
        m = folium.Map(location=location, zoom_start=zoom_start)
        folium.Marker(location).add_to(m)
        return st_folium(m, width=700, height=500)
    return None


def create_route_map(origin, destination, origin_coords, dest_coords):
    """
    Create a folium map showing route between two locations.

    Args:
        origin: Name of origin location (str)
        destination: Name of destination location (str)
        origin_coords: Tuple of (lat, lon) for origin
        dest_coords: Tuple of (lat, lon) for destination

    Returns:
        folium.Map object
    """
    # Create map centered between the two points
    midpoint = [(origin_coords[0] + dest_coords[0]) / 2,
                (origin_coords[1] + dest_coords[1]) / 2]

    m = folium.Map(location=midpoint, zoom_start=7)

    # Add markers
    folium.Marker(
        origin_coords,
        popup=origin,
        icon=folium.Icon(color='green', icon='flag')
    ).add_to(m)

    folium.Marker(
        dest_coords,
        popup=destination,
        icon=folium.Icon(color='red', icon='flag')
    ).add_to(m)

    # Add line between points
    folium.PolyLine(
        locations=[origin_coords, dest_coords],
        color='blue',
        weight=2.5,
        opacity=1
    ).add_to(m)

    return m


def display_route_map(origin, destination, origin_coords, dest_coords):
    """
    Display the route map in Streamlit.
    """
    map_obj = create_route_map(origin, destination, origin_coords, dest_coords)
    st_folium(map_obj, width=700, height=500)
