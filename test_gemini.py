from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("No GEMINI_API_KEY found in environment variables")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash-latest")
response = model.generate_content('Say hello in JSON: {"greeting":"Hello world"}')
print(response.text)
