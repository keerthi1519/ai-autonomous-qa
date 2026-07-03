from app.core.ai_client import ai_client

response = ai_client.generate(
    "Reply with exactly: Hello from Gemini!"
)

print(response)