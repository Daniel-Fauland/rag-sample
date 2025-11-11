# Ultimate FastAPI Starter Template

A production-ready FastAPI template that accelerates your backend development with best practices baked in. This template combines modern tooling, comprehensive error handling, performance optimizations, and developer-friendly features to help you build robust, scalable APIs faster.

### Why Choose This Template?

- 🚀 **Instant Productivity**: Skip weeks of boilerplate setup and jump straight into building your business logic
- 🛡️ **Production-Ready Security**: Built-in error handling, request validation, and environment management
- 📊 **Performance Optimized**: Configured for high performance with customizable workers, thread pools, and optimized event loops
- 🧪 **Testing Ready**: Integrated testing setup with pytest for both unit and integration tests
- 🐳 **Docker Support**: Ready-to-use containerization with optimized configurations
- 🔧 **Modern Tooling**: Uses `uv` for faster package management and includes essential development tools

Perfect for teams and developers who want to build production-grade FastAPI applications without compromising on quality or spending time on initial setup.

> [!TIP]
>
> **New here?** Check out the [Quick Start Guide](./backend/QUICKSTART.md) for a condensed getting-started experience!

**Content Overview**

- [Feature Overview](#feature-overview)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
  - [Automated Setup (Recommended)](#automated-setup-recommended)
  - [Manual Setup (Advanced)](#manual-setup-advanced)
    - [Postgres Database Setup](#postgres-database-setup)
      - [Local Postgres DB](#local-postgres-db)
      - [Online Postgres DB](#online-postgres-db)
    - [Database Migrations](#database-migrations)
    - [Redis Database setup](#redis-database-setup)
      - [Local Redis DB setup](#local-redis-db-setup)
      - [Online Redis DB setup](#online-redis-db-setup)
- [Running the Application](#running-the-application)
  - [Development Mode](#development-mode)
  - [Docker Mode](#docker-mode)
- [Common Commands](#common-commands)
- [Integration Tests](#integration-tests)
- [Env Variables Overview](#env-variables-overview)

## Feature Overview

This sample provides a FastAPI backend with the following features:

- [x] Using [uv](https://github.com/astral-sh/uv) as a package manager.
- [x] Central [config.py](./backend/config.py) file for all env variables and settings.
- [x] Immediate validation of variables inside of [config.py](./backend/config.py) using `pydantic-settings`.
- [x] `Pydantic` models for api route request/response validation.
- [x] Performance optimization (Customizable workers / customizable thread pool / faster event_loop with uvicorn[standard] / offloading of synchronous functions).
- [x] Global logging for the entire application. See [utils/logging.py](./backend/utils/logging.py).
- [x] Life span object with health checks at startup & clean-up at shutdown for FastAPI app instance. See [main.py](./backend/main.py).
- [x] Middleware with execution timer for api routes. See [middleware.py](./backend/middleware.py).
- [x] Global API error setup using custom error classes. See [errors.py](./backend/errors.py).
- [x] Colored terminal output support with `termcolor`. See [helper.py](./backend/utils/helper.py).
- [x] Integration tests. See [tests/](./backend/tests/).
- [x] Containerization of backend. See [Dockerfile](./backend/Dockerfile).
- [x] Postgres database integration. See [database/](./backend/database/)
- [x] Alembic database migrations. See [migrations/](./backend/migrations/)
- [x] User authentication using JWT. See [auth/jwt.py](./backend/auth/jwt.py)
- [x] User authorization using RBAC. See [auth/auth.py](./backend/auth/auth.py)
- [x] Redis Database integration. See [databse/redis.py](./backend/database/redis.py)
- [x] Using Redis for TTL based token blacklisting to handle JWT invalidation. See [auth/auth.py](./backend/auth/auth.py)
- [x] IP based rate limiting on individual api routes. See [api/health/router.py](./backend/api/health/router.py)
- [x] Streamlined setup with Makefile and Docker Compose for easy development

> TODO: Mock KeyVault env values

## Quick Start

Get up and running in under 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/Daniel-Fauland/rag-sample.git
cd rag-sample/backend

# 2. Run the automated setup (installs uv, creates .env, starts databases, runs migrations)
make setup

# 3. Update your JWT secret in .env
# Edit .env and set JWT_SECRET to a secure random string (at least 32 bytes)

# 4. Start the FastAPI backend
make run
```

That's it! 🎉 Your API is now running at [http://localhost:8000](http://localhost:8000)

**What `make setup` does:**

- ✅ Installs `uv` package manager (if not already installed)
- ✅ Creates `.env` file from template
- ✅ Starts Postgres and Redis databases in Docker
- ✅ Waits for databases to be healthy
- ✅ Runs all database migrations
- ✅ Inserts initial data (including 2 test users)

**Default test users** (available after setup):
| Email | Password | Role |
| ----------------- | ------------- | ----- |
| admin@example.com | Adminpassword | admin |
| user@example.com | Userpassword | user |

> [!TIP]
> Run `make help` to see all available commands!

## Prerequisites

**Required:**

- [Docker](https://www.docker.com/) installed and running
- Git for cloning the repository

**Optional (auto-installed by `make setup`):**

- [uv](https://github.com/astral-sh/uv) package manager (faster alternative to pip)

> [!NOTE]
> The `make setup` command will automatically install `uv` if it's not already available. On MacOS/Linux, it uses the official installer script. Windows users should install `uv` manually before running setup:
>
> ```powershell
> powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
> ```

## Installation & Setup

### Automated Setup (Recommended)

The easiest way to get started is using the provided Makefile commands (run from `backend/` directory):

```bash
cd backend

# One-command setup (creates .env, starts databases, runs migrations)
make setup

# Start the backend
make run
```

That's it! The application handles:

- ✅ Environment file creation
- ✅ Database provisioning (Postgres + Redis in Docker)
- ✅ Database migrations
- ✅ Initial data seeding

**Important:** After running `make setup`, edit `.env` and set your `JWT_SECRET` to a secure random string (at least 32 bytes).

> [!TIP]
> See all available commands with `make help`

### Manual Setup (Advanced)

If you prefer manual control or want to use cloud-hosted databases, follow these steps:

### Postgres Database Setup

#### Local Postgres DB

If you already have a postgres database running somewhere skip this step and go to [Online Postgres DB](#online-postgres-db) setup instead. <br/>
You can install postgres locally on your machine or via Docker. Docker is straightforward and the process is the same for all machines therefore setup with docker will be shown:

1. Make sure you have docker installed and the docker daemon is running.
2. Define some settings for your postgres db:

   ```
   export PG_VERSION="17.6"
   export PG_CONTAINER="db-be-pg"
   export PG_NAME="postgres"
   export PG_USER="systemuser"
   export PG_PASSWORD="mysecretpassword"
   export PG_NETWORK_NAME="db-be-pg-network"
   export PG_VOLUME="db-be-pg-data"
   ```

   **Important**: If you change these default values make sure to also adjust the `.env` file to ensure correct credentials for the backend application.

3. Get the postgres docker image. You can check the available versions [here](https://hub.docker.com/_/postgres):

   ```
   docker pull postgres:${PG_VERSION}
   ```

4. Create a docker network for your postgres db:

   ```
   docker network create ${PG_NETWORK_NAME}
   ```

5. Start the postgres instance:

   ```
   docker run --name ${PG_CONTAINER} --network ${PG_NETWORK_NAME} -p 5432:5432 -e POSTGRES_PASSWORD=${PG_PASSWORD} -e POSTGRES_DB=${PG_NAME} -e POSTGRES_USER=${PG_USER} -v ${PG_VOLUME}:/var/lib/postgresql/data -d postgres:${PG_VERSION}
   ```

6. Validate successful setup by connecting to it:

   ```
   docker run -it --rm --network ${PG_NETWORK_NAME} postgres psql -h ${PG_CONTAINER} -U ${PG_USER} -d ${PG_NAME}
   ```

   This will now prompt you for your password. Then you can test if your postgres db works properly by writing the following query:

   ```
   SELECT current_database(), current_user;
   ```

   (You can exit the postgres terminal session by simply typing `exit`.)

> [!Note]
> You can stop and remove the running postgres container with this command: `docker stop ${PG_CONTAINER} && docker rm ${PG_CONTAINER}` <br/>
> The next time you want to run the database you only have to run step 1, 2 & 5.

> [!Tip]
> You can now also connect to this database through any UI based database program like [pgAdmin](https://www.pgadmin.org) when providing the following credentials: <br/>
> Host name/address: `localhost` <br/>
> Port: `5432` <br/>
> Maintenance database: The value of: `${PG_NAME}` <br/>
> Username: The value of: `${PG_USER}` <br/>
> Password: The value of: `${PG_PASSWORD}`

#### Online Postgres DB

If you use a cloud hosted postgres db you only need the to update the following credentials in the `.env` file.

```
# --- Database Settings ---
DB_HOST="your-pg-db-domain.com"
DB_NAME="your-db-name"
DB_PASSWD="your-db-password"
DB_USER="your-db-user"
DB_PORT="your-db-port"
DB_SSL="True"  # Probably True in most cases
```

> [!Note]
> Make sure to check any potential ip/firewall resctrictions that might block your connection.

### Database Migrations

<details>
<summary>Creating the inital migration</summary>

> [!Note] >**Note:** This step has already been done. There is no action required from your side. This is only for documentation purposes.

Alembic is being used for DB migrations.
In order to set up initial migrations for an async DB run the following command:

```
uv run alembic init -t async migrations
```

The command above will create a migrations folder with some files in it. In order to make it work with a postgres database and pickup schema changes automatically some changes in [migrations/env.py](./migrations/env.py) and [migrations/script.py.mako](./migrations/script.py.mako) were necessary. All changes are marked with `# EDITED` within those files.

Then you can run the following command to create the inital migration:

```
uv run alembic revision --autogenerate -m "Initial migration including all tables"
```

> [!Note]
> Keep in mind that `--autogenerate` will compare your db models with you actual schema in you postgres db. If you already have some tables in you postgres db (e.g. you created them manually or before switching to alembic) they won't be added to the migrations as migrations will only cover changes from your current state to the defined state. If you want your initial migration to completely generate all tables make sure to delete the tables from your postgres db before running the alembic command.

</details>

**Applying Migrations**:

If you want to create a new migration after changing a model [schema](./backend/database/schemas/) run the following command:

```
uv run alembic revision --autogenerate -m "put_message_here"
```

If you want to create a new migration for chaning some data (e.g. filling an existing table with initial data) without schema changes run this command instead:

```
uv run alembic revision -m "put_message_here"
```

If you want to apply a migration and upgrade to the latest revision simply run the following command:

```
uv run alembic upgrade head
```

If you want to undo all migrations and return to a state before the very first migration run:

```
uv run alembic downgrade base
```

You can check the history of all revisions by running:

```
uv run alembic history
```

You can upgrade | downgrade either to a specific revision id by typing:

```
uv run alembic upgrade <revision_id>
uv run alembic downgrade <revision_id>
```

Or by upgrade | downgrade by a specific number of migrations:

```
uv run alembic upgrade -2
uv run alembic downgrade -2
```

> [!Note]
> 2 inital users for the application are already included with migration [3cb8a3670bf3](./backend/migrations/versions/3cb8a3670bf3_add_initial_data.py)
> The default credentials are:
>
> | Index | Email             | Password      |
> | ----- | ----------------- | ------------- |
> | 1     | admin@example.com | Adminpassword |
> | 2     | user@example.com  | Userpassword  |

### Redis Database setup

#### Local Redis DB setup

If you already have a redis database running somewhere skip this step and go to [Online Redis DB setup](#online-redis-db-setup) setup instead. <br/>
You can install redis locally on your machine or via Docker. Docker is straightforward and the process is the same for all machines therefore setup with docker will be shown:

1. Make sure you have docker installed and the docker daemon is running.
2. Define some settings for your redis db:

   ```
   export REDIS_VERSION="8.2"
   export REDIS_CONTAINER="db-be-redis"
   export REDIS_PASSWORD="mysecretpassword"
   export REDIS_NETWORK_NAME="db-be-redis-network"
   ```

   **Important**: If you change these default values make sure to also adjust the `.env` file to ensure correct credentials for the backend application.

3. Get the redis docker image. You can check the available versions [here](https://hub.docker.com/_/redis):

   ```
   docker pull redis:${REDIS_VERSION}
   ```

4. Create a docker network for your redis db:

   ```
   docker network create ${REDIS_NETWORK_NAME}
   ```

5. Start the redis instance:

   ```
   docker run --name ${REDIS_CONTAINER} --network ${REDIS_NETWORK_NAME} -p 6379:6379 -e REDIS_PASSWORD=${REDIS_PASSWORD} -d redis:${REDIS_VERSION} redis-server --requirepass ${REDIS_PASSWORD}
   ```

6. Validate successful setup by connecting to it:

   ```
   docker run -it --rm --network ${REDIS_NETWORK_NAME} redis:${REDIS_VERSION} redis-cli -h ${REDIS_CONTAINER} -a ${REDIS_PASSWORD}
   ```

   This will connect you to the Redis CLI. You can test if your redis db works properly by writing the following commands:

   ```
   ping
   set test "Hello Redis"
   get test
   ```

   (You can exit the redis terminal session by simply typing `exit`.)

> [!Note]
> You can stop and remove the running redis container with this command: `docker stop ${REDIS_CONTAINER} && docker rm ${REDIS_CONTAINER}` <br/>
> The next time you want to run the database you only have to run step 1, 2 & 5. <br/>
> Note: No persistent volume is used for Redis since this setup is intended for JWT token blacklisting, where data should be ephemeral and cleared when the container stops.

> [!Tip]
> You can now also connect to this database through any UI based database program like [RedisInsight](https://redis.com/redis-enterprise/redis-insight/) when providing the following credentials: <br/>
> Host name/address: `localhost` <br/>
> Port: `6379` <br/>
> Password: The value of: `${REDIS_PASSWORD}`

#### Online Redis DB setup

If you use a cloud hosted redis db you only need to update the following credentials in the `.env` file.

```
# --- Redis Settings ---
REDIS_HOST="your-redis-db-domain.com"
REDIS_PORT="your-redis-port"
REDIS_PASSWORD="your-redis-password"
```

> [!Note]
> Make sure to check any potential ip/firewall restrictions that might block your connection.

## Running the Application

### Development Mode

**Recommended for local development** - FastAPI runs locally with hot-reload, databases in Docker:

```bash
# Start databases (if not already running)
make db-start

# Start FastAPI backend
make run
```

The backend will be available at:

- API: [http://localhost:8000](http://localhost:8000)
- Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

> [!TIP] > **VSCode Python Interpreter Setup:**
>
> 1. Run the backend at least once to create the `.venv` folder
> 2. Open Command Palette (CMD/CTRL + SHIFT + P)
> 3. Select `Python: Select Interpreter`
> 4. Choose `Enter interpreter path...`
> 5. Navigate to `backend/.venv/bin/python` (or `backend/.venv/Scripts/python.exe` on Windows)

### Docker Mode

**Run the entire stack in Docker** - Useful for production-like testing:

```bash
# Run entire stack (backend + databases) in Docker
make run-docker

# Or run in background
make run-docker-bg
```

This builds and runs everything in containers. The backend will be available at [http://localhost:8000](http://localhost:8000)

To stop everything:

```bash
make stop
```

> [!NOTE]
> When running in Docker mode, the backend uses the `backend/Dockerfile` and connects to databases via Docker networking.

### Additional Tips

**Testing specific functions without starting the full backend:**

You can run individual Python modules directly:

```bash
cd backend
uv run -m <folder>.<file>
```

Example - test password hashing functionality:

```bash
cd backend
uv run -m utils.user
```

## Common Commands

Here are the most frequently used commands (run from `backend/` directory):

### Database Management

```bash
make db-start         # Start Postgres and Redis
make db-stop          # Stop databases
make db-restart       # Restart databases
make db-logs          # View database logs
make db-migrate       # Run migrations
make db-status        # Check database status
make postgres-cli     # Access Postgres CLI
make redis-cli        # Access Redis CLI
```

### Development

```bash
make run              # Run FastAPI locally
make dev              # Start DBs and get ready for development
make test             # Run all tests
make test-file FILE=tests/users/test_users.py  # Run specific test file
```

### Docker Operations

```bash
make run-docker       # Run entire stack in Docker (foreground)
make run-docker-bg    # Run entire stack in Docker (background)
make stop             # Stop all containers
```

### Utilities

```bash
make clean            # Clean up everything (containers, volumes, cache)
make help             # Show all available commands
```

> [!TIP]
> All Makefile commands include colored output and helpful status messages to guide you through the process.

## Integration Tests

This project includes comprehensive integration tests that test entire API endpoints (not just individual functions). The testing framework uses [pytest](https://docs.pytest.org/en/stable/) under the hood.

### Running Tests

**Run all tests:**

```bash
make test
```

**Run specific test files or folders:**

```bash
# Test specific folder
make test-file FILE=tests/users/

# Test specific file
make test-file FILE=tests/roles/test_roles.py
```

**Run tests directly:**

```bash
cd backend
uv run tests/run_tests.py                             # All tests
uv run tests/run_tests.py tests/users/                # Specific folder
uv run tests/run_tests.py tests/roles/test_roles.py   # Specific file
```

### Important Notes

- **Custom Test Runner**: This project uses a custom test wrapper (`tests/run_tests.py`) that:

  - Patches environment variables to use a separate test database
  - Tests Alembic migrations in isolation
  - **Never run `pytest` directly** - always use the custom wrapper

- **Test Database**: Tests automatically use a separate database (`pg_test_db` by default) to avoid interfering with your development data

- **Naming Convention**: All test files must start with `test_` to be discovered by pytest

- **Helper Functions**: Common test utilities are available in [tests/test_helper.py](./backend/tests/test_helper.py) (e.g., `login_user_with_type()`)

> [!TIP]
>
> - For examples of well-structured tests, see [tests/test/test_test.py](./backend/tests/test/test_test.py)
> - To add custom setup/teardown logic, edit [tests/run_tests.py](./backend/tests/run_tests.py) (placeholders provided)

## Env Variables Overview

Here is a complete overview about the environment variables in the `.env` file:

| Category             | ENV Variable                  | Default Value                      | Description                                                                                                  | Additional Information                                                            | Mandatory |
| -------------------- | ----------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- | --------- |
| Basic Settings       | LOGGING_LEVEL                 | INFO                               | The Logging level for the backend application                                                                | Must be either DEBUG, INFO, WARNING, ERROR, CRITICAL                              | NO        |
| Basic Settings       | FASTAPI_PROJECT_NAME          | FastAPI                            | The Project of you application used in the Swagger title                                                     |                                                                                   | NO        |
| Basic Settings       | FASTAPI_WELCOME_MSG           | Access the swagger docs at '/docs' | The default message shown when opening the fastapi url in the browser                                        |                                                                                   | NO        |
| Basic Settings       | FASTAPI_PORT                  | 8000                               | The port at which the fastapi (uvicorn) backend runs                                                         |                                                                                   | NO        |
| Basic Settings       | RATE_LIMIT_UNPROTECTED_ROUTES | 10                                 | How many requests a client (ip address) can make against the same API route per minute on unprotected routes |                                                                                   | NO        |
| Environment Settings | BACKEND_VERSION               | 0.0.1                              | The version of the fastapi backend                                                                           | Must be in format x.y.z (e.g. 1.2.3)                                              | NO        |
| Environment Settings | IS_LOCAL                      | False                              | Whether the backend runs on a local machine or somewhere else (e.g. Cloud instance)                          |                                                                                   | NO        |
| Environment Settings | IS_DOCKER                     | True                               | Whether the backend runs within a docker container                                                           |                                                                                   | NO        |
| User Settings        | DEFAULT_USER_ROLE             | user                               | The default role that is assigned at user creation. Can only assign roles that exist in the db.              |                                                                                   | NO        |
| Database Settings    | DB_HOST                       | -                                  | The host name of your SQL database                                                                           |                                                                                   | **YES**   |
| Database Settings    | DB_PORT                       | -                                  | The port on which your SQL database runs                                                                     | Must be an integer between 1 and 65535                                            | **YES**   |
| Database Settings    | DB_NAME                       | -                                  | The name of your database that you want to connect to                                                        |                                                                                   | **YES**   |
| Database Settings    | DB_PASSWD                     | -                                  | The password of your SQL database                                                                            |                                                                                   | **YES**   |
| Database Settings    | DB_USER                       | -                                  | The user that the application will use when interacting with the db                                          |                                                                                   | **YES**   |
| Database Settings    | DB_SSL                        | True                               | Whether the connection between app and db should be established using SSL                                    |                                                                                   | NO        |
| Database Settings    | DB_ECHO                       | True                               | Whether the backend should log its internal operations in the terminal                                       |                                                                                   | NO        |
| Database Settings    | DB_POOL_SIZE                  | 20                                 | Number of database connections to maintain in the pool                                                       | Core concurrency limit for database operations                                    | NO        |
| Database Settings    | DB_MAX_OVERFLOW               | 30                                 | Additional connections allowed when pool is full                                                             | Burst capacity for handling traffic spikes                                        | NO        |
| Database Settings    | DB_POOL_TIMEOUT               | 15                                 | Timeout in seconds waiting for available connection                                                          | Prevents application from hanging on connection requests                          | NO        |
| Database Settings    | DB_POOL_RECYCLE               | 3600                               | Recycle connections after this many seconds                                                                  | Prevents stale connections in long-running applications                           | NO        |
| Redis Settings       | REDIS_HOST                    | -                                  | The host name of your Redis database                                                                         |                                                                                   | **YES**   |
| Redis Settings       | REDIS_PORT                    | -                                  | The port on which your Redis database runs                                                                   | Must be an integer between 1 and 65535                                            | **YES**   |
| Redis Settings       | REDIS_PASSWORD                | -                                  | The password of your Redis database                                                                          |                                                                                   | **YES**   |
| Redis Settings       | REDIS_POOL_SIZE               | 20                                 | Number of database connections to maintain in the pool                                                       |                                                                                   | NO        |
| JWT Settings         | JWT_ALGORITHM                 | HS256                              | The JWT algorithm used for signing and verifying JWTs                                                        |                                                                                   | NO        |
| JWT Settings         | JWT_SECRET                    | -                                  | The JWT secret key used for de-/encoding JWTs                                                                | Must be at least 256 bits (32 bytes) long                                         | **YES**   |
| JWT Settings         | JWT_ACCESS_TOKEN_EXPIRY       | 15                                 | The life span of a generated access token in minutes                                                         | Must be an integer between 1 and 999                                              | NO        |
| JWT Settings         | JWT_REFRESH_TOKEN_EXPIRY      | 30                                 | The life span of a generated refresh token in days                                                           | Must be an integer between 1 and 999                                              | NO        |
| Performance Settings | THREAD_POOL                   | 80                                 | The amount of threads that can be open concurrently for each worker                                          | [More info](https://www.starlette.io/threadpool/)                                 | NO        |
| Performance Settings | WORKERS                       | 4                                  | The amount of workers the uvicorn server uses                                                                | Ideally this number is ~amount of CPU threads (not cores) for optimal scalability | NO        |
| Test Settings        | TEST_LOGGING_LEVEL            | ERROR                              | Logging level for the application during testing                                                             | Must be either DEBUG, INFO, WARNING, ERROR, CRITICAL                              | NO        |
| Test Settings        | TEST_DB_NAME                  | pg_test_db                         | The name of your test database that you want to connect to                                                   |                                                                                   | NO        |

> [!Note]
> Variables are only mandatory if **no default value** exists. They must be set in order to start the backend.
