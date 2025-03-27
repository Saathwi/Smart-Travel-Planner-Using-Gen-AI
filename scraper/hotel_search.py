import streamlit as st
from datetime import datetime, timedelta
from .hotel_api import HotelScraper
import json
from pathlib import Path


def show_hotel_search():
    # Navigation button at top with unique key
    if st.button("← Back to Chat", key="back_to_chat_top"):
        st.session_state.current_page = "chatbot_page"
        st.rerun()

    st.title("🏨 Hotel Search")

    # Initialize session state
    if "hotel_params" not in st.session_state:
        st.session_state.hotel_params = None

    # Load airport mapping
    try:
        with open(Path(__file__).parent / 'airport_mapping.json', 'r') as f:
            airport_mapping = json.load(f)
        all_destinations = sorted(list(airport_mapping.keys()))
    except Exception as e:
        st.error(f"Failed to load destinations: {str(e)}")
        all_destinations = ["mumbai", "delhi", "bangalore", "hyderabad",
                            "chennai", "kolkata", "goa", "pune"]

    # Search Form
    with st.form("hotel_form", clear_on_submit=False):
        cols = st.columns([1, 1, 1])
        with cols[0]:
            destination = st.selectbox(
                "City",
                options=all_destinations,
                index=all_destinations.index("mumbai") if "mumbai" in all_destinations else 0,
                key="hotel_destination_select"
            )
        with cols[1]:
            check_in = st.date_input(
                "Check-in",
                min_value=datetime.now(),
                value=datetime.now() + timedelta(days=7),
                key="hotel_checkin_date"
            )
        with cols[2]:
            nights = st.number_input(
                "Nights",
                min_value=1,
                max_value=30,
                value=3,
                key="hotel_nights_input"
            )

        budget = st.slider(
            "Max price per night (₹)",
            1000, 50000, 10000, 500,
            key="hotel_budget_slider"
        )
        min_rating = st.slider(
            "Minimum rating",
            1.0, 5.0, 4.0, 0.1,
            key="hotel_rating_slider"
        )

        # Form submit button
        submitted = st.form_submit_button("🔍 Search Hotels")
        if submitted:
            st.session_state.hotel_params = {
                "destination": destination,
                "check_in": check_in.strftime("%Y-%m-%d"),
                "nights": nights,
                "budget": budget,
                "min_rating": min_rating
            }

    # Display Results
    if st.session_state.hotel_params:
        params = st.session_state.hotel_params
        st.subheader(f"🏙️ {params['destination'].title()}")
        st.caption(f"📅 {datetime.strptime(params['check_in'], '%Y-%m-%d').strftime('%b %d, %Y')} • "
                   f"{params['nights']} nights • "
                   f"💰 Max ₹{params['budget']}/night • "
                   f"⭐ {params['min_rating']}+")

        with st.spinner("Searching hotels..."):
            scraper = HotelScraper()
            results = scraper.search_hotels(
                destination=params['destination'],
                check_in=params['check_in'],
                nights=params['nights'],
                budget=params['budget'],
                min_rating=params['min_rating']
            )

        if "error" in results:
            st.error(f"❌ {results['error']}")
        elif not results.get("hotels"):
            st.warning("No hotels found matching your criteria")
        else:
            for hotel in results["hotels"]:
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        # Fixed image display with use_container_width
                        st.image(
                            hotel.get("photo", "https://via.placeholder.com/300x200?text=No+Image"),
                            use_container_width=True
                        )
                    with col2:
                        st.subheader(hotel.get("name", "Hotel Name Not Available"))
                        st.markdown(f"**📍 {hotel.get('address', 'Address not available')}**")

                        # Display metrics with proper fallbacks
                        cols = st.columns(3)
                        cols[0].metric("Price", hotel.get("price", "N/A"))

                        # Handle rating display (convert to stars if needed)
                        rating = hotel.get("rating", "No rating")
                        if isinstance(rating, (int, float)):
                            rating = f"{rating:.1f}⭐"
                        cols[1].metric("Rating", rating)

                        # Handle reviews display
                        reviews = hotel.get("reviews")
                        cols[2].metric("Reviews", str(reviews) if reviews is not None else "N/A")

                        # Fixed link display
                        if hotel.get("link"):
                            st.markdown(
                                f'<a href="{hotel["link"]}" target="_blank" style="text-decoration:none;">'
                                f'<button style="background-color:#4CAF50;color:white;padding:0.5em 1em;'
                                f'border:none;border-radius:4px;">📖 View Details</button></a>',
                                unsafe_allow_html=True
                            )

                    st.divider()

    # Bottom navigation button with unique key
    if st.button("← Back to Chat", key="back_to_chat_bottom"):
        st.session_state.current_page = "chatbot_page"
        st.rerun()
