import os
import time
from openai import OpenAI, RateLimitError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY")
)

try:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      store=True,
      messages=[
        {"role": "user", "content": "write a haiku about ai"}
      ]
    )

    print(completion.choices[0].message)

except RateLimitError as err:
    print(f"RateLimitError occurred: {err}")
    print("You exceeded your current quota. Please check your plan and billing details.")
    print("Retrying in 30 seconds...")

    # Wait before retrying the request
    time.sleep(30)

    # Retry the request (optional)
    try:
        completion = client.chat.completions.create(
          model="gpt-4o-mini",
          store=True,
          messages=[
            {"role": "user", "content": "write a haiku about ai"}
          ]
        )

        print(completion.choices[0].message)

    except Exception as retry_err:
        print(f"An error occurred during retry: {retry_err}")