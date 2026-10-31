# CodePilot AI 🚀

**Live demo:** [codepilotai-frontend.onrender.com](https://codepilotai-frontend.onrender.com)

> **Evidence-grounded repository analysis for developers and teams**
> Understand a project's user value and engineering health, ask source-cited questions, and explore repository structure with a focused LangChain RAG workflow.

---

## ✨ Features

| Core workflow                       | Description                                                                        |
| ----------------------------------- | ---------------------------------------------------------------------------------- |
| **Project Assessment**              | Analyze user value and engineering characteristics with retrieved source citations |
| **Codebase Q&A**                    | Ask natural-language questions with answers linked to files and line ranges        |
| **Engineering Health**              | Review maintainability, architecture, complexity, and prioritized actions          |
| **Security Analysis**               | Inspect security, reliability, and bug findings                                    |
| **Production Readiness**            | Review release risks against repository evidence and detected operational files    |
| **Dependency Map**                  | Explore internal module relationships and external dependencies                    |
| **Developer Onboarding**            | Generate a practical guide for understanding the repository                        |
| **Repository Explorer**             | Index and inspect source files used as evidence                                    |
| **Sequence, Class & Flow Diagrams** | Render source-grounded Mermaid diagrams with evidence links                        |
| **Test Case Generator**             | Generate framework-aware runnable tests from a selected source file                |
| **PDF Export**                      | Download formatted analysis reports and generated test plans                       |

---

## 🛠 Tech Stack

| Layer    | Technology                                               |
| -------- | -------------------------------------------------------- |
| Frontend | Next.js 16, Tailwind CSS v4, ReactFlow, Mermaid.js       |
| Backend  | FastAPI, Python 3.11+, SQLAlchemy, LangChain, pgvector   |
| AI       | Google Gemini through LangChain chat and embeddings      |
| RAG      | LangChain splitting, PostgreSQL/pgvector retrieval, cited answers |
| Database | PostgreSQL (Neon recommended)                             |

---

## 📋 Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL with pgvector** (Neon is supported)
- **Google Gemini API Key** — Get one free at [aistudio.google.com](https://aistudio.google.com/app/apikey)
- **Git** (for cloning repositories)

---

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/CodePilotAI.git
cd CodePilotAI
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate venv (Windows)
.venv\Scripts\activate

# (macOS/Linux)
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and set DATABASE_URL to your Neon PostgreSQL URL and
# GEMINI_API_KEY to your Google Gemini API key.

# Start backend
python -m uvicorn main:app --reload --port 8000
```

> enOr use the included startup script: **double-click `start.bat`** in the `backend/` folder.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (optional)
copy .env.example .env.local
# Edit .env.local if backend runs on a different URL

# Start frontend
npm run dev
```

> Or use the included startup script: **double-click `start.bat`** in the `frontend/` folder.

### 4. Open in Browser

```
http://localhost:3000
```

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

| Variable          | Required | Default                    | Description                |
| ----------------- | -------- | -------------------------- | -------------------------- |
| `GEMINI_API_KEY`  | ✅ Yes   | —                          | Google Gemini API key      |
| `DATABASE_URL`    | ✅ Yes   | —                          | PostgreSQL/Neon connection URL; enables pgvector storage |
| `REDIS_URL`       | No       | `redis://localhost:6379/0` | Redis broker/backend URL for Celery; configure the hosted URL in the API and worker environments |
| `API_KEY`         | No       | _(blank)_                  | Protect backend endpoints  |
| `ALLOWED_ORIGINS` | No       | `http://localhost:3000`    | CORS allowed origins       |
| `REPOS_DIR`       | No       | `./repositories`           | Directory for cloned repos |
| `GEMINI_EMBEDDING_MODEL` | No | `gemini-embedding-001` | Gemini embedding model |
| `EMBEDDING_BATCH_SIZE` | No | `5` | Chunks sent in one embedding request |
| `EMBEDDING_TOKENS_PER_MINUTE` | No | `20000` | Shared database-coordinated token budget; set below your actual Gemini quota |
| `EMBEDDING_MAX_RETRIES` | No | `5` | Bounded retries for quota and temporary service/network errors |
| `EMBEDDING_INITIAL_BACKOFF` | No | `2` | Initial retry backoff in seconds |
| `EMBEDDING_MAX_BACKOFF` | No | `90` | Maximum exponential backoff in seconds |
| `EMBEDDING_BATCH_DELAY` | No | `1` | Delay between successful embedding batches in seconds |

### Frontend (`frontend/.env.local`)

| Variable                   | Required | Default                 | Description     |
| -------------------------- | -------- | ----------------------- | --------------- |
| `NEXT_PUBLIC_API_BASE_URL` | No       | `http://127.0.0.1:8000` | Backend API URL |

---

## 🔄 Using a Repository

1. Navigate to **Repositories** in the sidebar
2. Click **New Repository** and paste a GitHub URL
3. Click **Index Repository** — the system will clone and embed all files
4. Once indexed, select a focused workflow from the repository workspace

The backend uses LangChain for document splitting, Gemini chat/embeddings, and
PostgreSQL pgvector storage for source-cited Q&A and the product-and-engineering
assessment. The `vector` extension is enabled automatically when the backend
connects. Existing Chroma indexes are not migrated; re-index each repository to
populate its embeddings in PostgreSQL. Completed analyses and identical Q&A
requests are cached in the database; a successful re-index clears that repository's
cached results so future requests use the updated source.
Embedding calls are sent in configurable small batches and coordinated through a
shared PostgreSQL token budget. Token use is estimated from text length (roughly
one token per three characters), so this is deliberately conservative but cannot
exactly match Google's tokenizer or quota accounting. Temporary 429/server/network
errors receive bounded exponential retries and honor Google's retry delay when
provided. Completed vector batches are committed individually; retrying a paused
index job reuses those vectors and only embeds missing chunks. Configure the
budget below the actual quota for your Gemini project; exhausted retries pause
the job so it can be resumed once quota is available.

The sequence, class, and flow diagrams use retrieved repository chunks and link
back to their source files. Production readiness combines repository file
evidence with the engineering-health analysis; it does not claim that tests or
deployments were executed. Test Case Generator reads the selected source file,
uses the nearest project test-framework configuration when available, and
provides a downloadable candidate test file without running or writing it into
the repository. Analysis reports and repository conversations can be exported
as PDF.

---

## 🤖 LangChain RAG Flow

Repository Q&A and Project Assessment use the same indexed repository context:

```
Repository files → LangChain text splitter → Gemini embeddings → Neon/PostgreSQL pgvector
Question → repository-filtered retrieval → LangChain prompt chain → cited answer
```

Project Assessment covers user/product value and software-engineering characteristics, with retrieved files shown as evidence.

---

## 📁 Project Structure

```
CodePilotAI/
├── backend/
│   ├── app/
│   │   ├── ai/          # LangChain chat, embeddings, PostgreSQL vector search
│   │   ├── api/         # FastAPI routes
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Focused analysis, indexing, caching, and RAG services
│   │   └── database/    # DB connection
│   ├── main.py          # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   └── start.bat
├── frontend/
│   ├── app/
│   │   ├── components/  # Reusable UI components
│   │   ├── lib/         # API client
│   │   ├── repositories/ # All repository AI tool pages
│   │   └── ...          # Other pages (analysis, security, etc.)
│   ├── .env.example
│   └── start.bat
└── README.md
```

---

## 🐛 Troubleshooting

**Backend won't start:** Check that `.env` exists and `GEMINI_API_KEY` is set.

**"Module not found" errors:** Make sure you activated the `.venv` before running uvicorn.

**Frontend shows no data:** Verify `NEXT_PUBLIC_API_BASE_URL` points to the running backend and check the backend logs.

**Mermaid diagram errors:** Click "Open in Mermaid Live" to debug the generated syntax.

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.
