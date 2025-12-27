# ARGOS: Autonomous Repository Guardian & Operational Swarm

ARGOS is an intelligent, agentic system designed to act as your autonomous Site Reliability Engineer (SRE). It uses a swarm of specialized AI agents to scan repositories, audit dependencies, execute safe sandboxed code, and generate real, functional security patches for your codebase.

## 🚀 Key Features

*   **🕵️ Explorer**: Scans local or remote (GitHub) repositories to understand codebase structure and language.
*   **🛡️ Auditor**: Runs security tools (Bandit for Python, npm audit for Node) to identify vulnerabilities.
*   **🧠 Supervisor**: Orchestrates the swarm, plans missions, and routes blocking issues to humans.
*   **📦 Sandboxed Execution**: All code analysis and testing happens inside secure E2B sandboxes, ensuring safety.
*   **🛠️ Fix Generation**: Automatically generates functional code fixes for Python and JavaScript vulnerabilities.
*   **✅ Human-in-the-Loop**: Critical security fixes require manual approval via a dedicated UI modal.
*   **📥 Patch Downloads**: Approved fixes are exported as standard `.patch` files for easy application.
*   **📊 Live Telemetry**: Real-time tracking of Token Usage, Latency, and Cost ($).

## 🚀 Core Missions

ARGOS provides specialized autonomous missions:

1.  **🛡️ Security Scan**:
    *   **Goal**: Identify and fix security vulnerabilities (OWASP Top 10).
    *   **Tools**: Bandit (Python), npm audit (Node.js).
    *   **Action**: Generates functional code patches for review.

2.  **📦 Dependency Audit**:
    *   **Goal**: Analyze project dependencies for outdated or risky packages.
    *   **Tools**: pip-audit, npm audit.
    *   **Action**: Reports dependency health and suggests upgrades.

3.  **🐛 Bug Analysis**:
    *   **Goal**: Deep static analysis to find code quality issues and potential bugs.
    *   **Tools**: Pylint, ESLint (planned).
    *   **Action**: Provides a detailed report of code smells and refactoring opportunities.

4.  **⚡ Custom Task**:
    *   **Goal**: Execute natural language requests (e.g., "Refactor the login class").
    *   **Action**: The Agentic Swarm plans and executes the request in the sandbox.

## 🏗️ Architecture & Tech Stack

ARGOS is built on a battle-tested, modern stack designed for reliability and speed:

### Backend
*   **Core**: Python 3.10+, FastAPI (High-performance Async API)
*   **Orchestration**: LangGraph (Stateful multi-agent workflows)
*   **AI/LLM**: LangChain + Groq (OSS-120B) for <1s inference
*   **Runtime**: E2B Code Interpreter (Secure, cloud-based sandboxing)
*   **Communication**: WebSockets (Real-time agent streaming)

### Frontend
*   **Framework**: React 18 + Vite (Blazing fast build tool)
*   **Styling**: TailwindCSS (Utility-first styling)
*   **Visualization**: React Flow (Interactive Graph/DAG view of agent swarm)
*   **Terminal**: xterm.js (Live streaming terminal logs)
*   **Icons**: Lucide React

### Infrastructure
*   **Telemetry**: LangSmith (Traceability) + Custom Token Cost Tracking
*   **Security**: Environment-isolated process execution

## 🛠️ Setup Instructions

### Prerequisites
*   Python 3.10+
*   Node.js 16+
*   Git

### 1. Clone the Repository
```bash
git clone https://github.com/vyom-modi/ARGOS.git
cd ARGOS
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Configuration**:
Create a `.env` file in the `backend/` directory:
```
GROQ_API_KEY=your_groq_key
E2B_API_KEY=your_e2b_key
LANGSMITH_API_KEY=your_langsmith_key (Optional)
LANGCHAIN_TRACING_V2=true (Optional)
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

## 🏃‍♂️ Running the System

1.  **Start Backend**:
    ```bash
    # From project root
    python run_backend.py
    ```
    Backend runs on `http://localhost:8000`.

2.  **Start Frontend**:
    ```bash
    # In a new terminal, from frontend/
    npm run dev
    ```
    Frontend accessible at `http://localhost:5173`.

## 🎮 Usage Guide

### 1. 🛡️ Security Scan
**Goal**: Find vulnerabilities and generate fixes.
1.  Click **New Mission** -> **Security Scan**.
2.  Paste a target URL (e.g., `https://github.com/adeyosemanputra/pygoat`).
3.  **Approve**: When the Supervisor finds an issue, review the code diff and approve it.
4.  **Download**: Click the generated "Patch Available" button to save the `.patch` file locally.

### 2. 📦 Dependency Audit
**Goal**: Check for outdated or vulnerable packages.
1.  Click **New Mission** -> **Dependency Audit**.
2.  Target: Repo URL (e.g., `https://github.com/vuejs/vue`).
3.  **Result**: View realtime logs as the Auditor scans `requirements.txt` or `package.json`.

### 3. ⚡ Custom Task
**Goal**: Ask the Agent Swarm to do anything.
1.  Click **New Mission** -> **Custom Task**.
2.  Input: "Refactor the `models.py` file to use dataclasses" or "Explain the authentication flow in `auth.py`".
3.  **Result**: The Explorer and Executor agents will research the codebase and execute your request.

## 🤝 Contributing
Contributions are welcome! Please start a discussion or open an issue before making major changes.

## 📄 License
MIT License
