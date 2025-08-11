import requests

API_KEY = "AIzaSyBKXikvQAAj66HjxTwqolNTBKNw7Cc8GV4"  # Replace with your Gemini API key from https://aistudio.google.com/app/apikey

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    for model in data.get("models", []):
        print(model["name"])
else:
    print("Error:", response.status_code, response.text)
