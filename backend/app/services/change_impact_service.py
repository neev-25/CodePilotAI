from app.ai.llm import GeminiService
from typing import Dict, Any

class ChangeImpactService:
    @staticmethod
    def generate(repository: Any, file_path: str, proposed_change: str) -> Dict[str, str]:
        prompt = f"""
You are an expert Software Architect reviewing a repository named '{repository.name}'.
Analyze the following proposed change and generate a Change Impact / Blast Radius Analysis report.

Target File: {file_path}
Proposed Change: {proposed_change}

Provide a structured Markdown report answering:
1. **Downstream Impact**: What specific systems, components, or generic files will likely break if this file structurally shifts?
2. **Coupling Risks**: Are there tight couplings making this hazardous?
3. **Data & Schema Dependencies**: Does this affect databases, caches, or external API contracts?
4. **Recommended Tests**: What testing strategy should the reviewer mandate to prove this patch is safe?
"""
        impact_markdown = GeminiService.generate_content(prompt)
        return {"impact": impact_markdown}
