# list_gemini_models.py
import google.generativeai as genai

genai.configure(api_key="AIzaSyBIBdb98IbeMRgb3G00u7q5DEPN2Mh3bPI")

try:
    models = genai.list_models()
    print("Models available for your key:")
    for m in models:
        # Just print the model name
        print(m.name)
except Exception as e:
    print("Error:", e)
