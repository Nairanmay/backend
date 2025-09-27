import google.generativeai as genai

genai.configure(api_key="AIzaSyA2R3KxBZ0dQp97a6_-t0M1KssTalRLIb4")

response = genai.generate_content(
    model="models/gemini-flash-latest",  # Use a valid model from your list
    prompt="Write a short story about a startup founder."
)

print(response.result)
