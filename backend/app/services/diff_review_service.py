from app.ai.llm import GeminiService
from typing import Dict, Any

class DiffReviewService:
    @staticmethod
    def generate(repository: Any, diff_text: str) -> Dict[str, str]:
        prompt = f"""
You are an expert AI code reviewer analyzing a Git Diff for the repository '{repository.name}'.
Analyze the following diff and provide a structured, constructive code review. 

Include sections for:
1. **Summary of Changes**: What does this diff achieve?
2. **Logic & Correctness**: Are there any bugs, logical errors, or edge cases missed?
3. **Performance & Security**: Can this be optimized? Are there trailing vulnerabilities?
4. **Suggestions**: Concrete recommendations (snippets if necessary).

Return the response in raw cleanly formatted Markdown.

### Git Diff:
```diff
{diff_text}
```
"""
        review_markdown = GeminiService.generate_content(prompt)
        return {"review": review_markdown}
