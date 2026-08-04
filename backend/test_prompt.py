from app.ai.prompt_builder import PromptBuilder

search_results = {
    "documents": [[
        "def login_user(username, password):\n    pass"
    ]],
    "metadatas": [[
        {
            "path": "auth/login.py",
            "start": 1,
            "end": 10
        }
    ]]
}

prompt = PromptBuilder.build(
    "How does login work?",
    search_results,
)

print(prompt)