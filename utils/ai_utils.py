import os
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.llms import HuggingFaceEndpoint
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

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
    llm = HuggingFaceEndpoint(
        huggingfacehub_api_token=api_token,
        repo_id=repo_id,
        task=task
    )

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"chat_history": chat_history, "user_question": user_query})

    return response.strip()
