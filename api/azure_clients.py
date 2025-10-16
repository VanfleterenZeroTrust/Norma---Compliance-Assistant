import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_type = "azure"
openai.api_key = os.environ["LLM_API_KEY"]
openai.api_base = os.environ["LLM_ENDPOINT"]
openai.api_version = "2024-02-01"
model = os.environ["LLM_MODEL_NAME"]

async def chat_completion(messages):
    response = openai.ChatCompletion.create(
        engine=model,
        messages=messages,
        temperature=0.2,
        max_tokens=800
    )
    return response["choices"][0]["message"]["content"]
