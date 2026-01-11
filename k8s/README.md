# Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the FastAPI application stack.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Namespace: fastapi-app                    │ │
│  │                                                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │ │
│  │  │   Ingress    │  │     HPA      │  │   Migration Job  │   │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────────────┘   │ │
│  │         │                 │                                  │ │
│  │         ▼                 ▼                                  │ │
│  │  ┌──────────────────────────────┐                           │ │
│  │  │     Backend Deployment       │                           │ │
│  │  │    (FastAPI - 2+ replicas)   │                           │ │
│  │  │  ┌────────┐  ┌────────┐     │                           │ │
│  │  │  │ Pod 1  │  │ Pod 2  │ ... │                           │ │
│  │  │  └────────┘  └────────┘     │                           │ │
│  │  └──────────────────────────────┘                           │ │
│  │         │                 │                                  │ │
│  │         ▼                 ▼                                  │ │
│  │  ┌──────────────┐  ┌──────────────┐                         │ │
│  │  │  PostgreSQL  │  │    Redis     │                         │ │
│  │  │ (StatefulSet)│  │ (Deployment) │                         │ │
│  │  │     + PVC    │  │  (ephemeral) │                         │ │
│  │  └──────────────┘  └──────────────┘                         │ │
│  │                                                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
k8s/
├── base/                           # Base manifests (shared)
│   ├── kustomization.yaml          # Kustomize configuration
│   ├── namespace.yaml              # Namespace definition
│   ├── postgres/                   # PostgreSQL resources
│   │   ├── statefulset.yaml
│   │   ├── service.yaml
│   │   ├── pvc.yaml
│   │   └── secret.yaml
│   ├── redis/                      # Redis resources
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── secret.yaml
│   ├── backend/                    # FastAPI backend resources
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   └── hpa.yaml
│   ├── migrations/                 # Database migration job
│   │   └── job.yaml
│   └── ingress.yaml               # Ingress configuration
├── overlays/
│   ├── local/                      # Local development overlay
│   │   └── kustomization.yaml
│   └── production/                 # Production overlay
│       └── kustomization.yaml
└── README.md
```

## Prerequisites

- **kubectl** - Kubernetes CLI
- **Docker** - For building images
- **Local Cluster** (one of):
  - [minikube](https://minikube.sigs.k8s.io/)
  - [kind](https://kind.sigs.k8s.io/)
  - [Docker Desktop Kubernetes](https://www.docker.com/products/docker-desktop/)

## Quick Start (Local Development)

### 1. Start your local Kubernetes cluster

**Minikube:**
```bash
minikube start
```

**Kind:**
```bash
kind create cluster
```

### 2. Deploy the application

From the `backend/` directory:

```bash
# Build and deploy to local cluster
make k8s-local-up

# Check deployment status
make k8s-status

# Access the API (port forwarding)
make k8s-port-forward
```

The API will be available at http://localhost:8000

### 3. Run database migrations

```bash
make k8s-migrate
```

### 4. Tear down

```bash
make k8s-local-down
```

## Available Make Commands

| Command | Description |
|---------|-------------|
| `make k8s-build` | Build Docker image for Kubernetes |
| `make k8s-local-up` | Deploy to local cluster |
| `make k8s-local-down` | Remove local deployment |
| `make k8s-prod-up` | Deploy to production (with confirmation) |
| `make k8s-prod-down` | Remove production deployment |
| `make k8s-status` | Show deployment status |
| `make k8s-logs` | Stream backend logs |
| `make k8s-migrate` | Run database migrations |
| `make k8s-port-forward` | Forward port 8000 to localhost |
| `make k8s-shell` | Open shell in backend pod |
| `make k8s-restart` | Restart backend deployment |

## Manual Deployment

If you prefer not to use the Makefile:

```bash
# Build the Docker image
docker build -t fastapi-backend:latest ./backend

# Load image into local cluster (minikube)
minikube image load fastapi-backend:latest

# Apply the manifests
kubectl apply -k k8s/overlays/local

# Check status
kubectl get all -n fastapi-app
```

## Configuration

### Secrets (MUST be updated for production!)

The base manifests include placeholder secrets. **Never use these in production!**

**PostgreSQL Secret** (`k8s/base/postgres/secret.yaml`):
```yaml
POSTGRES_DB: postgres
POSTGRES_USER: systemuser
POSTGRES_PASSWORD: mysecretpassword  # CHANGE THIS!
```

**Redis Secret** (`k8s/base/redis/secret.yaml`):
```yaml
REDIS_PASSWORD: mysecretpassword  # CHANGE THIS!
```

**Backend Secret** (`k8s/base/backend/secret.yaml`):
```yaml
JWT_SECRET: replace-with-secure-secret-at-least-32-bytes  # CHANGE THIS!
```

### Creating Secrets Properly

For production, create secrets externally:

```bash
# Generate a secure JWT secret
JWT_SECRET=$(openssl rand -hex 32)

# Create secrets
kubectl create secret generic postgres-secret \
  --from-literal=POSTGRES_DB=mydb \
  --from-literal=POSTGRES_USER=myuser \
  --from-literal=POSTGRES_PASSWORD=$(openssl rand -base64 24) \
  -n fastapi-app

kubectl create secret generic redis-secret \
  --from-literal=REDIS_PASSWORD=$(openssl rand -base64 24) \
  -n fastapi-app

kubectl create secret generic backend-secret \
  --from-literal=JWT_SECRET=$JWT_SECRET \
  -n fastapi-app
```

Or use:
- [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets)
- [External Secrets Operator](https://external-secrets.io/)
- Cloud provider secret managers (AWS Secrets Manager, Azure Key Vault, etc.)

### ConfigMap Settings

The backend ConfigMap (`k8s/base/backend/configmap.yaml`) contains all non-sensitive configuration. Key settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `LOGGING_LEVEL` | INFO | Log verbosity |
| `FASTAPI_PORT` | 8000 | API port |
| `WORKERS` | 4 | Uvicorn workers |
| `DB_POOL_SIZE` | 20 | Database connection pool |
| `JWT_ACCESS_TOKEN_EXPIRY` | 15 | Token expiry (minutes) |

## Environment Overlays

### Local Overlay

Optimized for development:
- Single replica for backend
- Reduced resource limits
- 1Gi PostgreSQL storage
- NodePort service for easy access
- DEBUG logging

### Production Overlay

Optimized for production:
- 3+ replicas with HPA (up to 20)
- Full resource limits
- 50Gi PostgreSQL storage
- TLS-enabled Ingress
- Pod anti-affinity for HA
- WARNING logging
- SSL database connections

## Health Checks

| Component | Liveness | Readiness |
|-----------|----------|-----------|
| PostgreSQL | `pg_isready` | `pg_isready` |
| Redis | `redis-cli ping` | `redis-cli ping` |
| Backend | `GET /health` | `GET /health-db` |

## Scaling

The backend uses HorizontalPodAutoscaler:

```yaml
# Local: 1-3 replicas
# Production: 3-20 replicas
# Target: 70% CPU, 80% Memory
```

Manual scaling:
```bash
kubectl scale deployment backend -n fastapi-app --replicas=5
```

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl get pods -n fastapi-app

# Describe pod for events
kubectl describe pod <pod-name> -n fastapi-app

# Check logs
kubectl logs <pod-name> -n fastapi-app
```

### Database connection issues

```bash
# Check if PostgreSQL is running
kubectl get pods -n fastapi-app -l app.kubernetes.io/name=postgres

# Check PostgreSQL logs
kubectl logs -n fastapi-app -l app.kubernetes.io/name=postgres
```

### Migration failures

```bash
# Check migration job logs
kubectl logs -n fastapi-app job/db-migration

# Re-run migrations
make k8s-migrate
```

### Backend not accessible

```bash
# Check service
kubectl get svc backend -n fastapi-app

# Port forward directly
kubectl port-forward -n fastapi-app svc/backend 8000:8000
```

## Ingress Configuration

The default Ingress uses nginx ingress controller. Update the host in production:

```yaml
# k8s/overlays/production/kustomization.yaml
- patch: |-
    - op: replace
      path: /spec/rules/0/host
      value: api.yourdomain.com
```

Install nginx ingress controller:
```bash
# Minikube
minikube addons enable ingress

# kubectl
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

## Resource Requirements

### Local Development
| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| PostgreSQL | 100m | 250m | 128Mi | 256Mi |
| Redis | 50m | 100m | 64Mi | 128Mi |
| Backend | 100m | 500m | 128Mi | 512Mi |

### Production
| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| PostgreSQL | 500m | 2000m | 512Mi | 2Gi |
| Redis | 250m | 500m | 256Mi | 512Mi |
| Backend | 500m | 2000m | 512Mi | 2Gi |
