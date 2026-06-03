import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
print("Key loaded:", key[:10] + "...")

genai.configure(api_key=key)

model = genai.GenerativeModel("gemini-2.0-flash")

response = model.generate_content("Hello")
print(response.text)