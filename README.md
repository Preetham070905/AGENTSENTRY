# AGENTSENTRY

### Kernel-Level Security and Monitoring for AI Agent Execution

AGENTSENTRY is a Linux-based security and monitoring prototype designed to demonstrate controlled AI-agent execution, kernel-level filesystem restrictions, process monitoring, security event analysis, and explainability through a web dashboard.

It uses **Linux Landlock**, a Linux kernel security mechanism, to restrict selected filesystem modifications performed by a controlled agent process.

The application combines a Python FastAPI backend with a React dashboard to present execution information, filesystem events, security alerts, and enforcement explanations.

---

## Table of Contents

1. Overview
2. Features
3. System Architecture
4. Technology Stack
5. Project Structure
6. Prerequisites
7. Installation
8. Running the Application
9. Testing Landlock Enforcement
10. API Documentation
11. Understanding the Dashboard
12. How Landlock Enforcement Works
13. Logs and Generated Data
14. Troubleshooting
15. Security Scope and Limitations
16. Future Improvements

---

## 1. Overview

AI agents can interact with files, processes, and other system resources while executing tasks. Without appropriate restrictions, an agent may perform filesystem operations outside its intended working environment.

AGENTSENTRY explores how operating-system-level security mechanisms can help control these operations.

The project demonstrates:

- Controlled agent execution.
- Filesystem modification restrictions using Linux Landlock.
- Monitoring of filesystem and process activity.
- Recording of allowed and denied operations.
- Security event analysis.
- Rule-based explanations for enforcement decisions.
- Centralized visualization through a web dashboard.

## 2. Features

### Kernel-Level Filesystem Enforcement

- Uses Linux Landlock to enforce filesystem restrictions.
- Defines a designated workspace for controlled agent execution.
- Allows configured filesystem modifications inside the permitted workspace.
- Denies restricted filesystem modifications outside the permitted workspace.

### Agent Execution

- Executes a controlled Python agent workflow.
- Applies the configured sandbox policy before performing filesystem operations.
- Records execution status and enforcement results.

### Filesystem Monitoring

- Uses Watchdog to observe filesystem events.
- Records relevant file activity for security analysis.

### Process Monitoring

- Uses psutil to collect process-related information.
- Provides process monitoring information through the backend.

### Security Analysis

- Analyzes recorded monitoring events.
- Generates security alerts based on the implemented detection logic.

### Explainability

- Processes recorded Landlock enforcement events.
- Generates human-readable, rule-based explanations.
- Explains why a filesystem modification succeeded or was denied.

### Interactive Dashboard

- Displays agent execution information.
- Presents filesystem enforcement events.
- Shows monitoring information and security alerts.
- Displays explainability results.

---

## 3. System Architecture

AGENTSENTRY consists of three primary layers.

**Frontend Layer**

- React
- Vite
- Recharts
- Lucide React

**Backend Layer**

- Python
- FastAPI
- Uvicorn
- psutil
- Watchdog

**Kernel Security Layer**

- Linux Landlock
- Kernel-enforced filesystem restrictions
- Controlled agent execution

### Execution Workflow

1. The user starts the AGENTSENTRY backend and frontend.
2. The controlled agent workflow is launched.
3. The agent runner configures the Landlock ruleset.
4. The process applies the filesystem restrictions.
5. A permitted filesystem modification inside the workspace succeeds.
6. A restricted modification outside the workspace is denied by the Linux kernel.
7. Enforcement events are recorded in JSON Lines logs.
8. The explainability module processes recorded enforcement events.
9. FastAPI exposes the available information through API endpoints.
10. The React dashboard displays the monitoring and enforcement information.

---

## 4. Technology Stack

| Component             | Technology     |
| --------------------- | -------------- |
| Frontend              | React 18       |
| Frontend Build Tool   | Vite 5         |
| Charts                | Recharts       |
| Icons                 | Lucide React   |
| Backend               | Python         |
| API Framework         | FastAPI        |
| API Server            | Uvicorn        |
| Kernel Security       | Linux Landlock |
| Process Monitoring    | psutil         |
| Filesystem Monitoring | Watchdog       |
| Communication         | REST API       |

---

## 5. Project Structure

```text
AGENTSENTRY/
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── src/
│   ├── api.py
│   ├── agent_runner.py
│   ├── sandbox.py
│   ├── file_monitor.py
│   ├── process_monitor.py
│   ├── security_analyzer.py
│   └── xai_explainer.py
│
├── logs/
│
├── sandbox_workspace/
│
├── test_files/
│
├── test_landlock.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Important Files

| File                       | Description                                    |
| -------------------------- | ---------------------------------------------- |
| `src/api.py`               | FastAPI backend and API endpoints              |
| `src/agent_runner.py`      | Controlled agent execution workflow            |
| `src/sandbox.py`           | Landlock ruleset configuration and enforcement |
| `src/file_monitor.py`      | Filesystem event monitoring                    |
| `src/process_monitor.py`   | Process monitoring                             |
| `src/security_analyzer.py` | Security event analysis                        |
| `src/xai_explainer.py`     | Rule-based enforcement explanations            |
| `test_landlock.py`         | Standalone Landlock enforcement test           |
| `frontend/src/App.jsx`     | Main React dashboard                           |

---

## 6. Prerequisites

Before installing AGENTSENTRY, ensure that your system has the following:

| Requirement      | Version / Specification                       |
| ---------------- | --------------------------------------------- |
| Operating System | Ubuntu or compatible Linux                    |
| Architecture     | x86_64 for the current syscall implementation |
| Python           | 3.12 recommended                              |
| Node.js          | 20.19+ recommended                            |
| npm              | Compatible with installed Node.js             |
| Linux Kernel     | Landlock support required                     |

**Important:** The current sandbox implementation uses hardcoded Linux x86_64 syscall numbers. Other architectures require corresponding syscall implementations.

Landlock support depends on the Linux kernel version and configuration. The application checks the available Landlock ABI.

---

## 7. Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Preetham070905/AGENTSENTRY.git
```

Navigate into the project directory:

```bash
cd AGENTSENTRY
```

### Step 2: Create a Python Virtual Environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### Step 3: Install Backend Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

The backend dependencies include:

```text
fastapi
uvicorn
psutil
watchdog
```

### Step 4: Install Frontend Dependencies

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm ci
```

Return to the project root:

```bash
cd ..
```

### Step 5: Verify Landlock Support

Activate your virtual environment if it is not already active.

Check the available Landlock ABI:

```bash
python -m src.sandbox
```

If the module does not provide a standalone execution entry point, use the agent runner in the testing section to verify Landlock support.

---

## 8. Running the Application

AGENTSENTRY uses separate backend and frontend development servers.

Open two separate terminal windows.

### Terminal 1: Start the Backend

Navigate to the project root:

```bash
cd AGENTSENTRY
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Start FastAPI:

```bash
python -m uvicorn src.api:app --host 127.0.0.1 --port 8000
```

Backend URL:

[http://127.0.0.1:8000](http://127.0.0.1:8000)

Interactive API documentation:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Terminal 2: Start the Frontend

Navigate to the project root:

```bash
cd AGENTSENTRY
```

Start the Vite development server:

```bash
npm --prefix frontend run dev -- --host 0.0.0.0
```

Open the application in your browser:

[http://localhost:5173](http://localhost:5173)

**Keep both terminal windows running while using the application.**

To stop either development server, press:

```text
Ctrl + C
```

---

## 9. Testing Landlock Enforcement

AGENTSENTRY includes a standalone test script to verify the configured Landlock filesystem restrictions.

### Run the Landlock Test

From the project root, activate the Python virtual environment:

```bash
source .venv/bin/activate
```

Execute:

```bash
python test_landlock.py
```

### Expected Results

```text
PASS: write inside workspace was allowed
PASS: write outside workspace was denied (EACCES)
PASS: temporary test directory cleaned up
```

These results demonstrate that:

- A write operation inside the permitted workspace succeeds.
- A restricted write operation outside the workspace is denied.
- Temporary test data is cleaned up.

### Run the Controlled Agent Workflow

Execute:

```bash
python -m src.agent_runner
```

The runner performs a controlled execution and reports information such as:

- Execution ID.
- Execution status.
- Landlock ABI version.
- Sandbox activation status.
- Filesystem operation results.
- Allowed and denied operations.

### Generate Explainability Results

Execute:

```bash
python -m src.xai_explainer
```

The explainability module processes recorded enforcement events and generates rule-based explanations.

The generated explanations are stored in the project's logs directory.

---

## 10. API Documentation

AGENTSENTRY exposes its backend functionality through FastAPI.

Once the backend is running, access the interactive documentation:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Available Endpoints

| Endpoint                  | Description                    |
| ------------------------- | ------------------------------ |
| `/api/health`             | Backend health information     |
| `/api/dashboard`          | Dashboard information          |
| `/api/processes`          | Process monitoring information |
| `/api/events`             | Recorded monitoring events     |
| `/api/alerts`             | Security alerts                |
| `/api/enforcement-events` | Landlock enforcement events    |
| `/api/agents`             | Agent execution information    |
| `/api/xai-explanations`   | Explainability results         |

You can use the Swagger interface to inspect and test the available API endpoints.

---

## 11. Understanding the Dashboard

The React dashboard provides a centralized view of the information exposed by the backend.

Depending on the available data, the dashboard presents:

- Agent execution information.
- Process monitoring information.
- Filesystem monitoring events.
- Security alerts.
- Kernel enforcement events.
- Explainability results.

The enforcement section helps distinguish between permitted and denied filesystem modifications.

---

## 12. How Landlock Enforcement Works

Linux Landlock is a kernel security mechanism that allows applications to restrict the filesystem access rights of processes.

In AGENTSENTRY:

1. The sandbox module checks Landlock availability.
2. A ruleset is created.
3. Filesystem access categories are configured.
4. The designated workspace is added as an allowed path for the configured rights.
5. `PR_SET_NO_NEW_PRIVS` is applied.
6. The Landlock ruleset is enforced on the current process.
7. Subsequent restricted filesystem modifications outside the permitted workspace are denied by the kernel.

The current implementation focuses on selected filesystem modification permissions.

It does not currently restrict every filesystem read, execution, network operation, or system call.

---

## 13. Logs and Generated Data

AGENTSENTRY records execution and monitoring information in its logs directory.

Important log files include:

| Log File                   | Purpose                             |
| -------------------------- | ----------------------------------- |
| `enforcement_events.jsonl` | Recorded sandbox enforcement events |
| `xai_explanations.jsonl`   | Generated rule-based explanations   |
| `file_events.jsonl`        | Filesystem monitoring events        |
| `security_alerts.jsonl`    | Security analysis alerts            |

JSON Lines (`.jsonl`) stores individual JSON records on separate lines.

These records help inspect agent executions, enforcement outcomes, and security explanations.

---

## 14. Troubleshooting

### Problem 1: ModuleNotFoundError

Ensure that the Python virtual environment is activated:

```bash
source .venv/bin/activate
```

Run Python modules from the project root using:

```bash
python -m src.agent_runner
```

### Problem 2: Backend Connection Refused

Check whether FastAPI is running.

Start the backend:

```bash
python -m uvicorn src.api:app --host 127.0.0.1 --port 8000
```

### Problem 3: Frontend Dependencies Missing

Navigate to the project root and execute:

```bash
npm --prefix frontend install
```

### Problem 4: Landlock Not Supported

Check the Linux kernel version:

```bash
uname -r
```

Verify that your Linux kernel supports Landlock and that the required ABI is available.

### Problem 5: Port Already in Use

Check which process is using the backend or frontend port:

```bash
ss -ltnp
```

Stop the conflicting process or configure an alternative port.

---

## 15. Security Scope and Limitations

AGENTSENTRY is currently a prototype.

The following limitations are important:

- The current agent runner executes a predefined Python workflow rather than a fully autonomous LLM-based agent.
- Landlock restricts selected filesystem modifications; it does not currently block every file read, network operation, or system call.
- Landlock restrictions apply to the process where the ruleset is enforced and are inherited by its descendants, subject to Linux security rules.
- Independently launched processes are not automatically protected by the current implementation.
- The explainability module uses deterministic, rule-based logic rather than an LLM.
- The current implementation does not provide comprehensive syscall monitoring or automatic process termination.
- The current syscall implementation targets Linux x86_64.

The project demonstrates kernel-enforced filesystem restrictions and monitoring. It should not be considered a complete endpoint security solution.

---

## 16. Future Improvements

Potential future enhancements include:

- Integration with real AI agent frameworks.
- Background security service for controlled agent execution.
- Broader agent activity monitoring.
- More comprehensive filesystem access policies.
- Advanced security event correlation.
- Improved threat detection.
- Enhanced explainability and reporting.
- Support for additional Linux architectures.

---

## Contributing

Contributions, suggestions, and improvements are welcome.

If you find an issue or have an idea for improvement, feel free to open an issue or submit a pull request.

---

## License

No license has currently been specified for this repository.

---

**AGENTSENTRY — Exploring Kernel-Level Security for AI Agent Execution.**

---

**AGENTSENTRY — Exploring Kernel-Level Security for AI Agent Execution.**
