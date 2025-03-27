# utils/ai_utils.py
import os
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.llms import HuggingFaceEndpoint
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from utils.map_utils import get_coordinates
import re

# Load API token
load_dotenv()
api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
task = "text-generation"

template = """
You are a travel assistant chatbot. Provide travel-related information including flight bookings, hotel recommendations, maps, and other travel tips.

Chat history:
{chat_history}

User question:
{user_question}
"""

prompt = ChatPromptTemplate.from_template(template)


def get_response(user_query, chat_history):
    # First check if this is a map request
    map_match = re.search(r"(show|map|route) (from|between) (.+?) (to|and) (.+)", user_query, re.IGNORECASE)

    if map_match:
        origin = map_match.group(3).strip()
        destination = map_match.group(5).strip()

        # Try to get coordinates for both locations
        origin_coords = get_coordinates(origin)
        dest_coords = get_coordinates(destination)

        if origin_coords and dest_coords:
            return {
                "type": "map",
                "text": f"Here's the route from {origin} to {destination}:",
                "map_data": {
                    "origin": origin,
                    "destination": destination,
                    "origin_coords": origin_coords,
                    "dest_coords": dest_coords
                }
            }
        else:
            locations_not_found = []
            if not origin_coords:
                locations_not_found.append(origin)
            if not dest_coords:
                locations_not_found.append(destination)
            return f"Sorry, I couldn't find coordinates for: {', '.join(locations_not_found)}"

    # If not a map request, proceed with normal LLM response
    llm = HuggingFaceEndpoint(
        huggingfacehub_api_token=api_token,
        repo_id=repo_id,
        task=task
    )

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"chat_history": chat_history, "user_question": user_query})

    return response.strip()
