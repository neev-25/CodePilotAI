from app.ai.llm import GeminiClient

client = GeminiClient()

response = client.generate(
    "Explain what FastAPI is in one sentence."
)

print(response)