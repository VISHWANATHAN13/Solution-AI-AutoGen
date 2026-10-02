import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

api = os.getenv("OPENAI_API_KEY")

def get_llm():
    return {
        "config_list":[
            {
                "model":"gpt-4o-mini",
                "api_key":os.getenv("OPENAI_API_KEY")
            }
        ]
    }