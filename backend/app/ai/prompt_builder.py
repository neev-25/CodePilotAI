class PromptBuilder:

    @staticmethod
    def build(question: str, search_results: dict) -> str:

        documents = search_results.get("documents", [[]])[0]
        metadatas = search_results.get("metadatas", [[]])[0]

        context_parts = []

        for document, metadata in zip(documents, metadatas):

            context_parts.append(
                f"""
File: {metadata['path']}
Lines: {metadata['start']} - {metadata['end']}

{document}
"""
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are CodePilot AI.

You answer questions ONLY using the provided repository context.

Instructions:

- Explain clearly.
- Mention filenames.
- Mention functions/classes whenever possible.
- If multiple files are involved, explain how they relate.
- If the answer is not present in the repository,
  reply exactly:

I couldn't find that information in the indexed repository.

Repository Context

{context}

Question

{question}
"""

        return prompt