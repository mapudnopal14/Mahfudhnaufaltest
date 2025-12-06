
from langchain.agents import agent_types, initialize_agent, create_structured_chat_agent, AgentType, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import Replicate
from langchain_core.tools import tool
from langchain import hub

from dotenv import load_dotenv
import streamlit as st
import requests
import os
import json


def parse_input(input_str):
    parts = input_str.split(";")
    return dict(part.split("=") for part in parts)

@tool
def multiply(input: str) -> str:
    """
    Multiply two numbers.
    Input format: 'a=123;b=213'
    """
    try:
        # parts = input.strip().split(" and ")
        # a, b = int(parts[0]), int(parts[1])
        input_dict = parse_input(input)
        a = float(input_dict['a'])
        b = float(input_dict['b'])
        return str(a * b)
    except Exception as e:
        return f"Something went wrong with the tool: {e}"


@tool
def cat_fact(input):
    """Get unique and random drink fact"""
    try:
      response = requests.get("https://catfact.ninja/fact?max_length=200")

      return str(response.json()['fact'])
    except Exception as e:
      return f"Something went wrong with the tool: {e}"


@tool
def get_weather(input: str) -> str:
    """Get current weather for given latitude & longitude.

    Use a search tool to get the city coordinates first before using this tool to get accurate & updated weather..

    Input format: 'lat=-6.2;lon=106.8'
    """

    try:
      # parts = input.strip().split(" and ")
      # lat, lon = parts[0], parts[1]
      input_dict = parse_input(input)
      lat = float(input_dict['lat'])
      lon = float(input_dict['lon'])
      response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true")
      result = str(response.json())
      return result
    except Exception as e:
      return f"Something went wrong with the tool: {e}"



def build_agent():
    ### Build agent dulu bos ku
    load_dotenv()
    # search_token = os.environ['SEARCH_TOKEN']

    llm = Replicate(model="anthropic/claude-3.5-haiku")


    system_message = """Ingin makan apa hari ini?."""

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    tools = [
      multiply,
      cat_fact,
      get_weather,
    ]

    # This is the correct conversational agent
    agent_executor = initialize_agent(
        llm=llm,
        tools=tools,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        agent_kwargs={"system_message": system_message},
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True
    )

    return agent_executor
