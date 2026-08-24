from app.ai.llm import GeminiService
from typing import Dict, Any

class ArchitectureDriftService:
    @staticmethod
    def generate(repository: Any, constraint: str) -> Dict[str, str]:
        prompt = f"""
You are an expert Software Architect reviewing a repository named '{repository.name}'.
The architectural design constraint specified by the development team is:

**Constraint**: {constraint}

Analyze the constraints conceptually based on standard full-stack architectures. Note that since you are an LLM agent, you will evaluate logically if typical patterns inside {repository.name} violate this rule.
Identify elements structurally that might be violating this constraint (Architecture Drift).

Return a structured Markdown report answering:
1. **Drift Status**: Are there explicit code violations logically matching this drift?
2. **Impacted Components**: Which specific files or domains drift from the intended structure?
3. **Resolution Path**: How should a developer refactor the code to properly resolve this architectural decay?
"""
        drift_markdown = GeminiService.generate_content(prompt)
        return {"drift_report": drift_markdown}
