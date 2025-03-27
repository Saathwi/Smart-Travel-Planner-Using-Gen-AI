import streamlit as st
from utils.map_utils import show_map, get_coordinates, display_route_map
from utils.ai_utils import get_response
from auth import register_user, authenticate_user, load_users
import re
import json
from scraper.google_flights_scraper import FlightScraper
from scraper.hotel_search import show_hotel_search
from datetime import datetime

# Set page config must be the very first Streamlit command
st.set_page_config(
    page_title="Smart Travel Planner",
    page_icon="🌍",
    layout="wide"
)


def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()


if "current_page" not in st.session_state:
    st.session_state.current_page = "login"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def login_page():
    st.title("Login to Smart Travel Planner")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if not username.strip():
            st.warning("❗ Username cannot be empty.")
        elif not password.strip():
            st.warning("❗ Password cannot be empty.")
        else:
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.user = {"username": username}
                st.success("✅ Login successful!")
                navigate_to("chatbot_page")
            else:
                st.error("❌ Invalid username or password")

    if st.button("Sign Up"):
        navigate_to("signup")


def signup_page():
    st.title("Sign Up for Smart Travel Planner")
    new_username = st.text_input("Username", key="signup_username")
    new_password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")

    if st.button("Sign Up"):
        if not new_username.strip():
            st.warning("❗ Username cannot be empty.")
        elif not re.match(r"^[a-zA-Z0-9_]{3,}$", new_username):
            st.warning(
                "❗ Username must contain only letters, numbers, or underscores and be at least 3 characters long.")
        elif username_exists(new_username):
            st.warning("❗ Username already exists. Please choose a different username.")
        elif not new_password.strip():
            st.warning("❗ Password cannot be empty.")
        elif len(new_password) < 8 or not re.search(r"[A-Za-z]", new_password) or not re.search(r"\d", new_password):
            st.warning("❗ Password must be at least 8 characters long and include both letters and numbers.")
        elif not confirm_password.strip():
            st.warning("❗ Confirm Password cannot be empty.")
        elif new_password != confirm_password:
            st.error("❌ Passwords do not match!")
        else:
            success, message = register_user(new_username, new_password)
            if success:
                st.success("✅ Signup successful! You can now log in.")
                navigate_to("login")
            else:
                st.error(f"❌ {message}")

    if st.button("Back to Login"):
        navigate_to("login")


def username_exists(username):
    users = load_users()
    return any(user["username"] == username for user in users["users"])


def chatbot_page():
    st.sidebar.title(f"Welcome, {st.session_state.user['username']}! 🎉")
    st.sidebar.header("Search Flights & Hotels")

    # Flight Search Section
    st.sidebar.subheader("Flight Search")
    source = st.sidebar.text_input("From", key="source")
    destination = st.sidebar.text_input("To", key="destination")
    date = st.sidebar.date_input("Date", key="date")

    flight_col, hotel_col = st.sidebar.columns(2)

    with flight_col:
        if st.button("Find Flights"):
            if not source.strip() or not destination.strip():
                st.sidebar.warning("❗ Please enter both source and destination.")
            else:
                try:
                    searcher = FlightScraper()
                    results = searcher.get_flight_data(
                        source=source,
                        destination=destination,
                        date=date.strftime("%Y-%m-%d")
                    )

                    if "error" in results:
                        st.error(f"❌ {results['error']}")
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"Flight search failed: {results['error']}"
                        })
                    elif "flights" in results:
                        flight_messages = [
                            f"### ✈️ Flight Options from {source.title()} to {destination.title()} on {date.strftime('%Y-%m-%d')}",
                            f"#### [View All Results]({results['search_url']})\n"
                        ]

                        for idx, flight in enumerate(results["flights"], 1):
                            flight_messages.append(
                                f"**{idx}. {flight['airline']}** - {flight['price']}\n"
                                f"- ⏱ **Duration:** {flight['duration']}\n"
                                f"- ✈️ **Stops:** {flight['stops']}\n"
                                f"- [🔗 Book Now]({flight['booking_url']})\n"
                            )

                        full_message = "\n".join(flight_messages)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": full_message
                        })
                        st.sidebar.success(f"Found {len(results['flights'])} flights!")
                    else:
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": "No flights found for this route."
                        })

                    st.rerun()
                except Exception as e:
                    st.error(f"🚨 Flight search failed: {str(e)}")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"Sorry, I couldn't check flights. Error: {str(e)}"
                    })
                    st.rerun()

    # Hotel Search Section
    with hotel_col:
        if st.button("Find Hotels"):
            if not destination.strip():
                st.sidebar.warning("❗ Please enter a destination.")
            else:
                st.session_state.hotel_search_params = {
                    "destination": destination,
                    "check_in": date.strftime("%Y-%m-%d"),
                    "nights": 3,  # Default value
                    "budget": 10000,  # Default value
                    "min_rating": 4.0  # Default value
                }
                st.session_state.current_page = "hotel_search"
                st.rerun()

    st.sidebar.button("Logout", on_click=logout)

    # Main Chat Interface
    st.title("Smart Travel Planner")

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if isinstance(message["content"], dict) and message["content"].get("type") == "map":
                st.write(message["content"]["text"])
                display_route_map(
                    message["content"]["map_data"]["origin"],
                    message["content"]["map_data"]["destination"],
                    message["content"]["map_data"]["origin_coords"],
                    message["content"]["map_data"]["dest_coords"]
                )
            else:
                st.write(message["content"])

    # Chat input
    user_query = st.chat_input("How can I assist you with your travel plans?", key="chat_input")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        response = get_response(user_query, st.session_state.chat_history)

        if isinstance(response, dict) and response.get("type") == "map":
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
            with st.chat_message("assistant"):
                st.write(response["text"])
                display_route_map(
                    response["map_data"]["origin"],
                    response["map_data"]["destination"],
                    response["map_data"]["origin_coords"],
                    response["map_data"]["dest_coords"]
                )
        else:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
            with st.chat_message("assistant"):
                st.write(response)


def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.current_page = "login"
    st.session_state.chat_history = []
    st.success("🔒 Logged out successfully!")


# Main Page Router
if st.session_state.authenticated:
    if st.session_state.current_page == "hotel_search":
        show_hotel_search()
    else:
        chatbot_page()
else:
    if st.session_state.current_page == "login":
        login_page()
    elif st.session_state.current_page == "signup":
        signup_page()
