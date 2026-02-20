import os
from dotenv import load_dotenv
import litellm

load_dotenv()

model = os.getenv("MODEL_NAME")
api_key = os.getenv("OPENROUTER_API_KEY")

print(f"Model: {model}")
print(f"API Key: {api_key[:10]}...")

response = litellm.completion(
    model=model,
    api_key=api_key,
    messages=[{"role": "user", "content": "say hi"}]
)

print(response.choices[0].message.content)