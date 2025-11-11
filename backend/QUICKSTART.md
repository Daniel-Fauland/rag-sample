# Quick Start Guide

This is a condensed guide to get you up and running as quickly as possible.

## Prerequisites

- Docker installed and running
- Git (to clone the repository)

## Setup (First Time)

```bash
# 1. Clone and enter the project
git clone https://github.com/Daniel-Fauland/rag-sample.git
cd rag-sample/backend

# 2. Run automated setup
make setup

# 3. Set your JWT secret
# Edit .env and change JWT_SECRET to a secure random string
```

## Start Developing

```bash
# Start the backend (databases must be running)
make run
```

Your API is now available at:

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

## Daily Workflow

```bash
# Start databases (if not running)
make db-start

# Start backend
make run

# In another terminal - run tests
make test
```

## Common Commands

| Command         | Description                 |
| --------------- | --------------------------- |
| `make help`     | Show all available commands |
| `make setup`    | Complete initial setup      |
| `make run`      | Run FastAPI locally         |
| `make test`     | Run all tests               |
| `make db-start` | Start databases             |
| `make db-stop`  | Stop databases              |
| `make clean`    | Clean everything            |

## Default Test Users

| Email             | Password      | Role  |
| ----------------- | ------------- | ----- |
| admin@example.com | Adminpassword | admin |
| user@example.com  | Userpassword  | user  |

## Troubleshooting

**Databases not starting?**

```bash
make db-logs  # Check database logs
```

**Need to reset everything?**

```bash
make clean    # Remove all containers and volumes
make setup    # Start fresh
```

**Want to access database directly?**

```bash
make postgres-cli  # Access Postgres
make redis-cli     # Access Redis
```

For detailed documentation, see [README.md](../README.md)
