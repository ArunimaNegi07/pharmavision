import os

import google.generativeai as genai


api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise SystemExit(
        "Set GOOGLE_API_KEY or GEMINI_API_KEY before running this utility."
    )

genai.configure(api_key=api_key)

print("Available Gemini models supporting content generation:")
for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(f"- {model.name}")
