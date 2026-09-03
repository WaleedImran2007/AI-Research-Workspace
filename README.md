# AI Research Workspace

> An AI-powered research workspace for uploading, organizing, processing, and querying your research material using RAG, agentic workflows, and semantic search.

AI Research Workspace (AIRW) is a full-stack AI application designed to turn scattered research material into an interactive, searchable knowledge base.

Users can upload documents and media, organize them into collections, and ask questions about their research. AIRW processes the uploaded content, creates searchable chunks and embeddings, retrieves the most relevant information, and uses an LLM to generate grounded answers with source information.

The project was built to understand and implement the underlying AI architecture rather than relying entirely on high-level abstractions.

---

## ✨ Features

### 📚 Knowledge Management

* Create and manage research collections
* Upload and organize research material
* Store document metadata and processed content
* Search across individual documents or entire collections

### 🤖 AI-Powered Research

* Retrieval-Augmented Generation (RAG)
* Semantic vector search
* Keyword-based retrieval
* Hybrid retrieval
* Query planning and intent detection
* Context-aware answer generation
* Source-aware responses

### 📄 Multi-Format Processing

AIRW can process different types of research material, including:

* PDF documents
* DOCX documents
* Audio files
* Images

Audio files can be transcribed and converted into searchable chunks, allowing users to ask questions about recorded conversations, lectures, interviews, or other audio material.

### 🔎 Source-Aware Retrieval

Answers can be traced back to the underlying research material.

For example, retrieved information can contain metadata such as:

* Document name
* Document type
* Page number
* Chunk information
* Audio timestamps

This makes it possible to navigate from an AI-generated answer back to the original source.

### 🧠 Agentic Workflow

Instead of treating every query as a simple vector-search operation, AIRW uses an intelligent workflow to determine how a query should be handled.

The system can:

1. Understand the user's query
2. Detect the query intent
3. Determine whether planning is required
4. Extract relevant filters
5. Resolve documents and collections
6. Retrieve relevant information
7. Provide context to the LLM
8. Generate the final response

This architecture allows the system to evolve beyond a basic chatbot into a more capable AI research assistant.

---

# 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │      Frontend       │
                         │   React / Vite      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │       Backend       │
                         └──────────┬──────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
        ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
        │  AI / Agent  │    │  Documents   │    │    Auth      │
        │   Workflow   │    │  Processing  │    │    System    │
        └──────┬───────┘    └──────┬───────┘    └──────────────┘
               │                   │
               ▼                   ▼
        ┌──────────────┐    ┌──────────────┐
        │  Retrieval   │    │   Supabase   │
        │    System    │    │   Storage    │
        └──────┬───────┘    └──────────────┘
               │
               ▼
        ┌──────────────┐
        │   MongoDB    │
        │ Vector Search│
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │     LLM      │
        │     Groq     │
        └──────────────┘
```

---

# 🧠 RAG Pipeline

The core research workflow follows a retrieval-augmented generation architecture.

```text
User Query
    │
    ▼
Query / Intent Analysis
    │
    ▼
Filter Extraction
    │
    ▼
Filter Resolution
    │
    ▼
Hybrid Retrieval
 ┌──┴──────────────┐
 │                 │
 ▼                 ▼
Vector Search   Keyword Search
 │                 │
 └───────┬─────────┘
         ▼
   Relevant Chunks
         │
         ▼
    Context Builder
         │
         ▼
        LLM
         │
         ▼
   Grounded Answer
         │
         ▼
      Sources
```

The system stores embeddings alongside chunk metadata, allowing retrieved information to remain connected to its original document.

---

# 🎧 Audio Processing

Audio research material follows a dedicated processing pipeline:

```text
Audio File
    │
    ▼
Audio Transcription
    │
    ▼
Transcript
    │
    ▼
Chunking
    │
    ▼
Embeddings
    │
    ▼
MongoDB Vector Search
```

Audio chunks can retain timestamp information such as:

```text
startTime: 0
```

This allows retrieved audio content to be associated with the relevant point in the recording.

---

# 🛠️ Tech Stack

## Frontend

* React
* Vite
* Tailwind CSS

## Backend

* Python
* FastAPI
* Pydantic

## AI / RAG

* LangChain
* LangGraph
* Hugging Face Embeddings
* BAAI/bge-small-en-v1.5
* Groq
* MongoDB Atlas Vector Search

## Database & Storage

* MongoDB Atlas
* Supabase Storage

## Authentication

* JWT-based authentication

## Infrastructure

* Docker
* Docker Compose
* Kubernetes
* Helm

## Development & Observability

* GitHub
* LangSmith

---

# 🐳 Docker

AIRW is containerized using Docker.

The backend can be built and run as a container:

```bash
docker build -t airw-backend .
```

```bash
docker run --env-file .env -p 8000:8000 airw-backend
```

The project also includes containerization/deployment configuration for running AIRW in a Kubernetes environment.

---

# ☸️ Kubernetes

The current deployment architecture supports Kubernetes.

The project includes Kubernetes manifests and Helm configuration for deploying the backend.

Example:

```bash
helm upgrade --install airw ./airw-chart -n airw
```

This makes the project suitable for experimenting with container orchestration, deployments, services, scaling, and production-style infrastructure.

---

# 📁 Project Structure

```text
AI-Research-Workspace/
│
├── frontend/
│
├── backend/
│   ├── routers/
│   ├── utils/
│   ├── services/
│   ├── tools/
│   └── ...
│
├── airw-chart/
│   ├── templates/
│   ├── Chart.yaml
│   └── values.yaml
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

> The exact structure may evolve as the project develops.

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/WaleedImran2007/AI-Research-Workspace.git
cd AI-Research-Workspace
```

## 2. Configure environment variables

Create a `.env` file containing the required credentials and configuration.

Example:

```env
MONGO_URI=
SUPABASE_URL=
SUPABASE_KEY=

JWT_SECRET=
ADMIN_EMAIL=

GROQ_API_KEY=
HF_TOKEN=

LANGSMITH_API_KEY=
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=AI Research Workspace
```

Never commit your `.env` file to GitHub.

## 3. Run with Docker

```bash
docker build -t airw-backend .
```

```bash
docker run --env-file .env -p 8000:8000 airw-backend
```

The frontend can be run separately during development.

---

# 🔐 Authentication

AIRW uses JWT-based authentication to protect user-specific resources.

Users can manage their own research collections and documents while backend authorization ensures that resources are associated with the appropriate user.

---

# 📊 Vector Search

Research chunks are converted into vector embeddings using:

```text
BAAI/bge-small-en-v1.5
```

The embedding dimension is:

```text
384
```

These embeddings are stored in MongoDB Atlas and queried using MongoDB Atlas Vector Search.

---

# 🎯 Why I Built This

AI Research Workspace was built as a practical exploration of how modern AI applications work under the hood.

Instead of treating RAG, agents, retrieval, planning, and execution as black boxes, the project focuses on understanding how these components interact within a complete application.

The project combines:

* Full-stack development
* AI engineering
* RAG
* Agentic workflows
* Vector search
* Document processing
* Authentication
* Cloud storage
* Docker
* Kubernetes
* Helm

This makes AIRW both an AI application and an ongoing engineering learning project.

---

# 🔮 Future Improvements

Planned improvements include:

* More advanced multi-agent workflows
* Automated research tasks
* Email-triggered agents
* Website form automation
* Payment-status monitoring
* Accounting/balance query agents
* Automated user provisioning
* Permission and rights-assignment workflows
* More advanced multimodal retrieval
* Improved source navigation
* Audio timeline-based source navigation

---

# 👨‍💻 Author

**Waleed Imran**

BS Computer Science student focused on:

**Agentic AI + Full-Stack Engineering**

GitHub: `WaleedImran2007`

---

## ⭐ Project Status

AIRW is an actively evolving project.

The architecture, AI workflows, and deployment infrastructure continue to be improved as new capabilities are added.
