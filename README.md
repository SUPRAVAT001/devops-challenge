# DevOps Challenge: Cloud-Native Microservice & CI/CD Pipeline

A containerized, resilient Python Flask microservice with PostgreSQL persistence, declarative Kubernetes orchestration on Minikube, and an automated self-hosted GitHub Actions CI/CD deployment pipeline.

---

## 1. Project Overview & Objectives

This project implements an end-to-end cloud-native microservice architecture demonstrating core DevOps engineering practices:

- **Microservice Decoupling**: Separation of application presentation/logic from relational persistence.
- **Production-Grade WSGI Runtime**: Flask application served via Gunicorn for concurrent request handling.
- **Health & Readiness Orchestration**: Multi-tier probes (`pg_isready` for PostgreSQL and `/health` for backend) guaranteeing zero traffic routing to unready pods during rolling updates.
- **High Availability**: Multi-replica backend deployment with load balancing through Kubernetes `ClusterIP` services.
- **Secrets Decoupling**: Sensitive database credentials abstracted from application manifests into Kubernetes Secrets.
- **Automated CI/CD Automation**: GitHub Actions workflow executed on a self-hosted runner performing syntax verification, container compilation, image side-loading, dynamic manifest tagging, and rollout status validation.

---

## 2. System Architecture & Workflow

### Architecture Diagram

```
                             Kubernetes Cluster (Minikube)
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│   Incoming Traffic                                                               │
│          │                                                                       │
│          ▼                                                                       │
│   ┌───────────────┐                                                              │
│   │ Service       │  (ClusterIP: 5000)                                           │
│   │ name: backend │                                                              │
│   └───────┬───────┘                                                              │
│           │                                                                      │
│           ├────────────────────────────┐                                         │
│           ▼                            ▼                                         │
│   ┌─────────────────────┐      ┌─────────────────────┐                           │
│   │ Pod: backend-xxxx-1 │      │ Pod: backend-xxxx-2 │                           │
│   │ ┌─────────────────┐ │      │ ┌─────────────────┐ │                           │
│   │ │ Gunicorn WSGI   │ │      │ │ Gunicorn WSGI   │ │                           │
│   │ │ Flask API :5000 │ │      │ │ Flask API :5000 │ │                           │
│   │ └────────┬────────┘ │      │ └────────┬────────┘ │                           │
│   └──────────┼──────────┘      └──────────┼──────────┘                           │
│              │                            │                                      │
│              └──────────────┬─────────────┘                                      │
│                             │ DB Connection (psycopg2)                           │
│                             ▼                                                    │
│                    ┌────────────────┐                                            │
│                    │ Service        │  (ClusterIP: 5432)                         │
│                    │ name: postgres │                                            │
│                    └────────┬───────┘                                            │
│                             ▼                                                    │
│                    ┌─────────────────────────┐                                   │
│                    │ Pod: postgres           │                                   │
│                    │ ┌─────────────────────┐ │     ┌────────────────────────┐    │
│                    │ │ PostgreSQL 16 Alpine│ │◄────┤ Secret                 │    │
│                    │ │ Port :5432          │ │     │ name: postgres-secret  │    │
│                    │ └─────────────────────┘ │     │ - DB_USER              │    │
│                    └─────────────────────────┘     │ - DB_PASSWORD          │    │
│                                                    └────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### CI/CD Deployment Workflow

```
[ Developer ]
      │  git push origin main
      ▼
[ GitHub Repository ]
      │  Webhook / Event Trigger
      ▼
[ Self-Hosted GitHub Runner ]
      │
      ├─► 1. Checkout Code (actions/checkout@v4)
      │
      ├─► 2. Test & Validate (python3 -m py_compile app/app.py)
      │
      ├─► 3. Build Container (docker build -t devops-challenge-api:${GITHUB_SHA} ./app)
      │
      ├─► 4. Minikube Ingestion (minikube image load devops-challenge-api:${GITHUB_SHA})
      │
      ├─► 5. Dynamic Manifest Tagging (sed replacement with ${GITHUB_SHA} in k8s/backend.yaml)
      │
      ├─► 6. Kubernetes Secret Injection (kubectl create secret generic postgres-secret)
      │
      ├─► 7. Manifest Deployment (kubectl apply -f k8s/postgres.yaml && kubectl apply -f k8s/backend.yaml)
      │
      ├─► 8. Rollout Validation (kubectl rollout status deployment/postgres & deployment/backend)
      │
      └─► 9. Verification & Inspection (kubectl get pods && kubectl get services)
```

---

## 3. Technology Stack

| Domain | Technology / Component | Version / Specification | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Runtime** | Python | `3.12-slim` | Execution environment for the microservice |
| **Web Framework** | Flask | `3.1.1` | REST API routing and JSON response handling |
| **WSGI Server** | Gunicorn | `23.0.0` | Production HTTP server binding `0.0.0.0:5000` |
| **Database Driver** | psycopg2-binary | `2.9.10` | PostgreSQL client adapter for database pooling |
| **Database Engine** | PostgreSQL | `16-alpine` | Relational database tier |
| **Container Engine** | Docker | Linux x86_64 | Container packaging and build platform |
| **Orchestrator** | Kubernetes (Minikube) | `v1.35.x` | Declarative container scheduling & scaling |
| **CI/CD Platform** | GitHub Actions | Self-hosted runner | Continuous integration and deployment pipeline |

---

## 4. Project Directory Structure

```text
devops-challenge/
├── .github/
│   └── workflows/
│       └── main.yml         # GitHub Actions automated build and deployment pipeline
├── .gitignore               # Excludes bytecode, environments, and runner artifacts
├── app/
│   ├── Dockerfile           # Multi-stage optimized Python 3.12-slim container build
│   ├── app.py               # Flask application logic, DB connectivity, and health probe
│   └── requirements.txt     # Locked application dependencies (Flask, Gunicorn, psycopg2)
├── k8s/
│   ├── backend.yaml         # Kubernetes Deployment (2 replicas) & ClusterIP Service
│   ├── postgres.yaml        # PostgreSQL Deployment (1 replica), probes & ClusterIP Service
│   └── secret.yaml          # Template secret manifest for DB_USER and DB_PASSWORD
└── README.md                # Technical system documentation
```

---

## 5. API Endpoints

The API operates on port `5000` inside the container and via Kubernetes Service `backend`:

### 1. Root Endpoint (`GET /`)
Returns general service identification and version metadata.

- **URL**: `GET /`
- **Response Code**: `200 OK`
- **Response Format**: `application/json`
- **Sample Response**:
  ```json
  {
    "application": "devops-challenge-api",
    "status": "running",
    "version": "2.0"
  }
  ```

### 2. Health & Readiness Probe (`GET /health`)
Evaluates end-to-end database connectivity. Used directly by Kubernetes `livenessProbe` and `readinessProbe`.

- **URL**: `GET /health`
- **Success (Database Connected)**:
  - **Status**: `200 OK`
  - **Payload**:
    ```json
    {
      "database": "connected",
      "status": "healthy"
    }
    ```
- **Failure (Database Unreachable / Disconnected)**:
  - **Status**: `503 Service Unavailable`
  - **Payload**:
    ```json
    {
      "database": "disconnected",
      "status": "unhealthy"
    }
    ```

---

## 6. Configuration & Environment Variables

All parameters are configurable via environment variables and Kubernetes manifests:

| Variable | Scope | Default Value | Kubernetes Injection | Description |
| :--- | :--- | :--- | :--- | :--- |
| `DB_HOST` | Backend API | `localhost` | `value: postgres` | Hostname/DNS name of PostgreSQL service |
| `DB_PORT` | Backend API | `5432` | `value: "5432"` | Listening port of PostgreSQL instance |
| `DB_NAME` | Backend & DB | `appdb` | `value: appdb` | Database catalog name |
| `DB_USER` | Backend & DB | `appuser` | `secretKeyRef: DB_USER` | Authenticated database user name |
| `DB_PASSWORD` | Backend & DB | `apppassword` | `secretKeyRef: DB_PASSWORD` | Database user authentication credential |

---

## 7. Prerequisites

Before running or deploying the project, ensure the following tooling is installed:

- **Linux / macOS environment** (or WSL2 on Windows)
- **Docker Engine**: `24.0+`
- **Kubernetes CLI (`kubectl`)**: Compatible with cluster version
- **Minikube**: `v1.30+`
- **Python**: `3.12+` (for local development outside containers)

---

## 8. Setup & Execution Guide

### Option A: Local Development (Bare Metal / Virtualenv)

1. Navigate to the application directory:
   ```bash
   cd /home/sdash/devops-challenge/app
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

4. Run PostgreSQL locally (e.g. via Docker):
   ```bash
   docker run -d --name local-postgres \
     -e POSTGRES_DB=appdb \
     -e POSTGRES_USER=appuser \
     -e POSTGRES_PASSWORD=apppassword \
     -p 5432:5432 \
     postgres:16-alpine
   ```

5. Launch the application with Gunicorn:
   ```bash
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=appdb
   export DB_USER=appuser
   export DB_PASSWORD=apppassword
   gunicorn --bind 0.0.0.0:5000 app:app
   ```

6. Verify locally in another terminal:
   ```bash
   curl -s http://127.0.0.1:5000/
   curl -s http://127.0.0.1:5000/health
   ```

---

### Option B: Docker Container Execution

1. Build the standalone Docker image:
   ```bash
   cd /home/sdash/devops-challenge
   docker build -t devops-challenge-api:latest ./app
   ```

2. Create a bridge network for inter-container communication:
   ```bash
   docker network create devops-net
   ```

3. Run PostgreSQL on the network:
   ```bash
   docker run -d --name postgres --network devops-net \
     -e POSTGRES_DB=appdb \
     -e POSTGRES_USER=appuser \
     -e POSTGRES_PASSWORD=apppassword \
     postgres:16-alpine
   ```

4. Run the API container on the same network:
   ```bash
   docker run -d --name backend --network devops-net \
     -p 5000:5000 \
     -e DB_HOST=postgres \
     -e DB_PORT=5432 \
     -e DB_NAME=appdb \
     -e DB_USER=appuser \
     -e DB_PASSWORD=apppassword \
     devops-challenge-api:latest
   ```

5. Validate container responses:
   ```bash
   curl -i http://localhost:5000/
   curl -i http://localhost:5000/health
   ```

---

### Option C: Declarative Kubernetes Deployment (Minikube)

1. Ensure Minikube is running:
   ```bash
   minikube start --driver=docker
   ```

2. Build and load the Docker image into the Minikube environment:
   ```bash
   cd /home/sdash/devops-challenge
   docker build -t devops-challenge-api:1.1 ./app
   minikube image load devops-challenge-api:1.1
   ```

3. Apply the database secret:
   ```bash
   kubectl apply -f k8s/secret.yaml
   ```

4. Deploy the PostgreSQL persistence tier:
   ```bash
   kubectl apply -f k8s/postgres.yaml
   kubectl rollout status deployment/postgres --timeout=120s
   ```

5. Deploy the backend API tier:
   ```bash
   kubectl apply -f k8s/backend.yaml
   kubectl rollout status deployment/backend --timeout=120s
   ```

6. Verify cluster resources:
   ```bash
   kubectl get pods -l app=postgres
   kubectl get pods -l app=backend
   kubectl get svc
   ```

7. Access the application via port-forwarding:
   ```bash
   kubectl port-forward svc/backend 5000:5000
   ```

   In another terminal:
   ```bash
   curl -s http://127.0.0.1:5000/
   curl -s http://127.0.0.1:5000/health
   ```

---

### Option D: Automated CI/CD Pipeline (GitHub Actions)

The repository includes an automated pipeline in `.github/workflows/main.yml` configured for a self-hosted runner:

1. **Prerequisites in GitHub Repository Settings**:
   - Register self-hosted runner under repository **Settings &rarr; Actions &rarr; Runners**.
   - Configure Action Secrets under **Settings &rarr; Secrets and variables &rarr; Actions**:
     - `DB_USER`: `appuser`
     - `DB_PASSWORD`: `apppassword`

2. **Triggering the Pipeline**:
   - Every push to the `main` branch automatically triggers the workflow.

3. **Workflow Execution Steps**:
   - Compiles Python syntax to catch errors prior to container build.
   - Builds container image tagged with `${GITHUB_SHA}`.
   - Sideloads the newly built image directly into Minikube.
   - Updates `k8s/backend.yaml` container image dynamically using `sed`.
   - Generates and applies `postgres-secret` using GitHub Secrets.
   - Deploys manifests and blocks until `kubectl rollout status` confirms healthy deployment.

---

## 9. Testing & Health Verification

### 1. Code Syntax & Compilation Verification
Verify syntax integrity without external dependencies:
```bash
python3 -m py_compile /home/sdash/devops-challenge/app/app.py
```

### 2. Pod Rollout Health
Inspect Kubernetes deployment progression:
```bash
kubectl rollout status deployment/postgres
kubectl rollout status deployment/backend
```

### 3. Kubernetes Probe Validation
Check probe status directly from container logs and pod descriptions:
```bash
kubectl describe pod -l app=backend | grep -E "Liveness|Readiness"
```

Expected probe configuration:
- **Backend Readiness**: HTTP GET `/health` on `:5000` (initialDelay: 10s, period: 5s, timeout: 3s)
- **Backend Liveness**: HTTP GET `/health` on `:5000` (initialDelay: 20s, period: 10s, timeout: 3s)
- **Postgres Readiness**: `pg_isready -U appuser -d appdb` (initialDelay: 5s, period: 5s)
- **Postgres Liveness**: `pg_isready -U appuser -d appdb` (initialDelay: 15s, period: 10s)

### 4. Database Failure Simulation (Resilience Test)
Scale PostgreSQL to 0 replicas to confirm the backend accurately reports unhealthiness:
```bash
kubectl scale deployment/postgres --replicas=0
# Once postgres stops, query backend:
curl -i http://127.0.0.1:5000/health
# Expected: HTTP/1.1 503 SERVICE UNAVAILABLE with {"database": "disconnected", "status": "unhealthy"}

# Restore database:
kubectl scale deployment/postgres --replicas=1
# Once postgres recovers, backend readiness probe restores HTTP 200 traffic routing.
```

---

## 10. Security & Operational Guardrails

- **Secret Decoupling**: Database credentials are never hard-coded in Dockerfiles or application code. Kubernetes Secrets provide secure environment variable injection via `secretKeyRef`.
- **Git Exclusions (`.gitignore`)**:
  - `actions-runner/`: Local runner tokens, RSA keys, and diagnostic dumps are strictly ignored.
  - `.env` & `.venv/`: Local virtual environments and environment secrets are prevented from being committed.
  - `__pycache__/` & `*.pyc`: Compiled Python bytecode is excluded.
- **Minimal Attack Surface**: The container runtime uses `python:3.12-slim` with `--no-cache-dir` flag to eliminate unnecessary build dependencies.
