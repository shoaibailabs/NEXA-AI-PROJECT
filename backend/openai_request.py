

from openai import OpenAI
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Get OpenRouter API key
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not openrouter_api_key:
    raise ValueError("OPENROUTER_API_KEY is missing from .env")

# OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key
)


def send_request(chat_history):

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=chat_history
    )

    answer = response.choices[0].message.content

    if not answer:
        print("Not understood clearly")

    return answer.strip()


# from openai import OpenAI
# import os
# # from user_config import openai_key

# from dotenv import load_dotenv
# load_dotenv()
# openai_key=os.getenv('openai_key')


# client=OpenAI(api_key=openai_key)

# def send_request(chat_history):

#     response = client.responses.create(
#         model="gpt-5.4-mini",
#         input=chat_history
#     )

#     answer = response.output_text.strip()

#     if not answer:
#         print("not understand clearly")

#     return answer
