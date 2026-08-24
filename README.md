# CodePilot AI 🚀

> **AI-powered GitHub Repository Analysis Platform**  
> Unlock architecture diagrams, security analysis, code review, test generation, and 19+ AI workflows — powered by Google Gemini & ChromaDB RAG.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Semantic Search** | Ask questions about any codebase in natural language |
| **Architecture Analysis** | AI-generated architecture explanations and diagrams |
| **Sequence & Class Diagrams** | Mermaid diagrams with hand-drawn sketch canvas |
| **Security Analysis** | Vulnerability and risk assessment |
| **Complexity Analysis** | Code complexity, debt, and smells |
| **Dependency Graph** | Visualize file and module dependencies |
| **Health Score** | Consolidated codebase health report |
| **README Generator** | Auto-generate professional README.md |
| **PR & Commit Writer** | AI-assisted pull request descriptions and commit messages |
| **Test Generator** | Generate unit tests for existing code |
| **Refactoring Advisor** | Actionable refactoring suggestions |
| **LLM Auto-Failover** | Automatic fallback across Gemini models on quota exhaustion |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, Tailwind CSS v4, ReactFlow, Mermaid.js |
| Backend | FastAPI, Python 3.11+, SQLAlchemy, ChromaDB |
| AI | Google Gemini 2.5 Flash (with multi-model failover) |
| Embeddings | Sentence Transformers |
| Database | SQLite (default), PostgreSQL (optional) |

---

## 📋 Prerequisites

- **Python** 3.11+
- **Node.js** 18+
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
# Edit .env and set GEMINI_API_KEY=your_key_here

# Start backend
python -m uvicorn main:app --reload --port 8000
```

> Or use the included startup script: **double-click `start.bat`** in the `backend/` folder.

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

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | — | Google Gemini API key |
| `DATABASE_URL` | No | `sqlite:///./codepilot.db` | Database connection string |
| `API_KEY` | No | _(blank)_ | Protect backend endpoints |
| `ALLOWED_ORIGINS` | No | `http://localhost:3000` | CORS allowed origins |
| `REPOS_DIR` | No | `./repositories` | Directory for cloned repos |

### Frontend (`frontend/.env.local`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | No | `http://127.0.0.1:8000` | Backend API URL |

---

## 🔄 Using a Repository

1. Navigate to **Repositories** in the sidebar
2. Click **New Repository** and paste a GitHub URL
3. Click **Index Repository** — the system will clone and embed all files
4. Once indexed, click any AI Tool card to analyze

---

## 🤖 LLM Model Failover

The backend automatically rotates through Gemini models when a quota limit is hit:

```
gemini-2.5-flash → gemini-2.0-flash → gemini-1.5-flash → gemini-1.5-pro
```

No manual intervention required.

---

## 📁 Project Structure

```
CodePilotAI/
├── backend/
│   ├── app/
│   │   ├── ai/          # Gemini client, RAG, scanner
│   │   ├── api/         # FastAPI routes
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic (30+ services)
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

**Frontend shows no data:** Open Settings (`/settings`) and verify the API endpoint is correct, then click "Test Connection".

**Mermaid diagram errors:** Click "Open in Mermaid Live" to debug the generated syntax.

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.
