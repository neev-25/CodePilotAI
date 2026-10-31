"""
Golden Q&A dataset for RAG evaluation.

Every entry is a dict with:
  question        – the question posed to the RAG pipeline
  expected_answer – the ground-truth answer (written by hand, derived from source)
  context_docs    – list of verbatim code snippets that a good retrieval should return
"""

GOLDEN_DATASET = [
    {
        "question": "Where are repository embeddings stored?",
        "expected_answer": (
            "Repository embeddings are stored in the repository_embeddings "
            "PostgreSQL table using pgvector and GoogleGenerativeAIEmbeddings."
        ),
        "context_docs": [
            (
                "VectorStore stores repository chunks in the repository_embeddings "
                "PostgreSQL table using the pgvector extension and Gemini embeddings. "
                "The connection comes from DATABASE_URL."
            )
        ],
    },
    {
        "question": "How does RAGService build the context prompt?",
        "expected_answer": (
            "RAGService calls PromptBuilder build with the question and search results "
            "to construct a prompt that includes file paths, line numbers, and code snippets."
        ),
        "context_docs": [
            (
                "RAGService asks a question by first calling SearchService search "
                "to retrieve results, then passes those results to PromptBuilder build "
                "which constructs a prompt including file paths and line numbers."
            ),
            (
                "PromptBuilder build creates context parts for each document by "
                "combining the file path, start and end line numbers, and code snippets "
                "into a single prompt string with the question appended."
            ),
        ],
    },
    {
        "question": "What retry strategy does GeminiClient use?",
        "expected_answer": (
            "GeminiClient has MAX_RETRIES of 3 and RETRY_DELAY of 3 seconds. "
            "It iterates through FALLBACK_MODELS and retries on 500 and 503 errors."
        ),
        "context_docs": [
            (
                "GeminiClient defines MAX_RETRIES as 3 and RETRY_DELAY as 3 seconds. "
                "It iterates through a list of FALLBACK_MODELS and retries the request "
                "when it encounters 500 or 503 errors from the Gemini API."
            )
        ],
    },
]
