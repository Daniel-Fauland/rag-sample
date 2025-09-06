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

**Content Overview**

- [Feature Overview](#feature-overview)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
  - [Postgres Database Setup](#postgres-database-setup)
    - [Local Postgres DB](#local-postgres-db)
    - [Online Postgres DB](#online-postgres-db)
  - [Database Migrations](#database-migrations)
  - [Run the Backend](#run-the-backend)
    - [Run Locally](#run-locally)
    - [Run with Docker](#run-with-docker)
- [Integration Tests](#integration-tests)
- [Env Variables Overview](#env-variables-overview)

## Feature Overview

This sample provides a FastAPI backend with the following features:

- [x] Using [uv](https://github.com/astral-sh/uv) as a package manager.
- [x] Central [config.py](./backend/config.py) file for all env variables and settings.
- [x] Immediate validation of variables inside of [config.py](./backend/config.py) using `pydantic-settings`.
- [x] `Pydantic` models for api route request/response validation.
- [x] Global logging for the entire application. See [utils/logging.py](./backend/utils/logging.py).
- [x] Life span object with health check at startup for FastAPI app instance. See [main.py](./backend/main.py).
- [x] Middleware with execution timer for api routes. See [middleware.py](./backend/middleware.py).
- [x] Global API error setup using custom error classes. See [errors.py](./backend/errors.py).
- [x] Performance optimization (Customizable workers / customizable thread pool / faster event_loop with uvicorn[standard] / offloading of synchronous functions). See `.env` file.
- [x] Colored terminal output support with `termcolor`. See [helper.py](./backend/utils/helper.py).
- [x] Integration tests. See [tests/](./backend/tests/).
- [x] Containerization of backend. See [Dockerfile](./backend/Dockerfile).
- [x] Postgres database integration. See [database/](./backend/database/)
- [x] Alembic database migrations. See [migrations/](./backend/migrations/)
- [ ] User authentication using JWT
- [ ] User authorization using RBAC

> TODO: User authentication using JWT <br/>
> TODO: User authorization <br/>
> TODO: Integration test using test db <br/>

## Prerequisites

- Clone this git repo
  ```
  git clone https://github.com/Daniel-Fauland/rag-sample.git
  ```
- The python backend uses [uv](https://github.com/astral-sh/uv) as a package manager instead of pip / conda.

  To install `uv` follow these steps:

  - **MacOS / Linux**:

  ```
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  - **Windows**:

  ```
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

- Create a `.env` file from the provided template and fill out all placeholder values with your credentials
  ```
  cd backend && cp .env.example .env
  ```
- You need a PostgresDB database. The database can be hosted locally or on the cloud.
- After you set up your database make sure to run the alembic migrations to create the necessary tables and fill with inital data.

## Installation & Setup

In order to install & run the application you need to do the following steps:

- Setup up postgres database ([local](#local-postgres-db) or [online](#online-postgres-db))
- Run database migrations in order to create the necessary tables and insert inital data
- Install & run the backend ([local](#run-the-backend-locally) or [docker](#run-the-backend-with-docker))

### Postgres Database Setup

#### Local Postgres DB

If you already have a postgres database running somewhere skip this step and go to [Online Postgres DB](#online-postgres-db) setup instead. <br/>
You can install postgres locally on your machine or via Docker. Docker is straightforward and the process is the same for all machines therefore setup with docker will be shown:

1. Make sure you have docker installed and the docker daemon is running.
2. Define some settings for your postgres db:

   ```
   export PG_VERSION="17.6"
   export PG_CONTAINER="db-be-pg"
   export PG_NAME="backend"
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
alembic init -t async migrations
```

The command above will create a migrations folder with some files in it. In order to make it work with a postgres database and pickup schema changes automatically some changes in [migrations/env.py](./migrations/env.py) and [migrations/script.py.mako](./migrations/script.py.mako) were necessary. All changes are marked with `# EDITED` within those files.

Then you can run the following command to create the inital migration:

```
alembic revision --autogenerate -m "Initial migration including all tables"
```

> [!Note]
> Keep in mind that `--autogenerate` will compare your db models with you actual schema in you postgres db. If you already have some tables in you postgres db (e.g. you created them manually or before switching to alembic) they won't be added to the migrations as migrations will only cover changes from your current state to the defined state. If you want your initial migration to completely generate all tables make sure to delete the tables from your postgres db before running the alembic command.

</details>

**Applying Migrations**:

If you want to create a new migration after changing a model [schema](./backend/database/schemas/) run the following command:

```
alembic revision --autogenerate -m "put_message_here"
```

If you want to create a new migration for chaning some data (e.g. filling an existing table with initial data) without schema changes run this command instead:

```
alembic revision -m "put_message_here"
```

If you want to apply a migration and upgrade to the latest revision simply run the following command:

```
alembic upgrade head
```

If you want to undo all migrations and return to a state before the very first migration run:

```
alembic downgrade base
```

You can check the history of all revisions by running:

```
alembic history
```

You can upgrade | downgrade either to a specific revision id by typing:

```
alembic upgrade <revision_id>
alembic downgrade <revision_id>
```

Or by upgrade | downgrade by a specific number of migrations:

```
alembic upgrade -2
alembic downgrade -2
```

> [!Note]
> 2 inital users for the application are already included with migration [8340e034cd24](./backend/migrations/versions/8340e034cd24_insert_inital_user_data.py)
> The default credentials are:
>
> | Index | Email             | Password      |
> | ----- | ----------------- | ------------- |
> | 1     | admin@example.com | Adminpassword |
> | 2     | user@example.com  | Userpassword  |

### Run the Backend

#### Run Locally

Make sure you have fulfilled all the prerequisites before proceeding. <br/>
In order to run a python project using `uv` simply run the following command within the `backend/` directory:

```
uv run main.py
```

This will start the fastapi backend. It can be accessed in the browser by going to this url: [localhost:8000](http://localhost:8000/) <br/>
Swagger docs are available at: [localhost:8000/docs](http://localhost:8000/docs)

> [!Tip]
> If you want to link your VSCode interpreter to the created venv for proper syntax highlighting follow these steps:
>
> 1. Run the backend at least once to create the `.venv` folder within the backend
> 2. Navigate to `backend/.venv/bin` and copy the path of the python binary
> 3. Open the VSC Command Palette CMD + SHIFT + P (or CTRL + SHIFT + P for Windows) and enter the option `Python: Select Interpreter`
> 4. Click on `Enter interpreter path...` and paste the python binary path

#### Run With Docker

In order to use this application with docker make sure [docker](https://www.docker.com/) is installed and running.

Go to the `backend` folder in a new linux like terminal (For Windows: Use `git bash` for example) and run:

```
./run_docker.sh
```

Backend will run on [http://localhost:8000/](http://localhost:8000/)

> [!Note]
> In case you want to build & start the docker image manually instead of using the shell script simplly run the following commands:
>
> Build: `docker build -t fastapi-server .` <br/>
> Run: `docker run -p 8080:8080 -e IS_DOCKER=True fastapi-server`

#### Additional Tips

If you want to test a specific function/file without starting the backend or even having a dedicated API route for it you can do so by calling a specific file directly like this:

```
uv run -m <folder>.<file>
```

An example can be found [here](./backend/utils/user.py) to simply test the hashing functionality:

```
uv run -m utils.user
```

## Integration Tests

This backend sample also features Integration tests. This means that instead of testing only a specific method you can test an entire endpoint. Unit tests can also be added in the same way if needed. Under the hood the testing framework [pytest](https://docs.pytest.org/en/stable/) is used.
You can simply run the tests by calling this method from within the `backend/` directory:

```
uv run tests/run_tests.py
```

Keep in mind that every test file within the [tests](./backend/tests/) directory must start with the prefix `test_` otherwise it won't be picked up by the `pytest` library.

> [!Tip]
> In case you need to execute any code before or after your tests you can simply edit the [run_tests.py](./backend/tests/run_tests.py) file and add your custom logic there. Placeholders have already been prepared. <br/>
> If you are unfamiliar with writing tests have a look at [./test/test_test.py](./backend/tests/test/test_test.py)

## Env Variables Overview

Here is an overview about the environment variables in your `.env` file:

| Category             | ENV Variable        | Default Value                      | Description                                                                         | Additional Information                                                            | Mandatory |
| -------------------- | ------------------- | ---------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | --------- |
| Basic Settings       | LOGGING_LEVEL       | INFO                               | The Logging level for the backend application                                       | Must be either DEBUG, INFO, WARNING, ERROR, CRITICAL                              | NO        |
| Basic Settings       | FASTAPI_WELCOME_MSG | Access the swagger docs at '/docs' | The default message shown when opening the fastapi url in the browser               |                                                                                   | NO        |
| Basic Settings       | FASTAPI_PORT        | 8000                               | The port at which the fastapi (uvicorn) backend runs                                |                                                                                   | NO        |
| Environment Settings | BACKEND_VERSION     | 0.0.1                              | The version of the fastapi backend                                                  | Must be in format x.y.z (e.g. 1.2.3)                                              | NO        |
| Environment Settings | IS_LOCAL            | False                              | Whether the backend runs on a local machine or somewhere else (e.g. Cloud instance) |                                                                                   | NO        |
| Environment Settings | IS_DOCKER           | True                               | Whether the backend runs within a docker container                                  |                                                                                   | NO        |
| Database Settings    | DB_HOST             | -                                  | The host name of your SQL database                                                  |                                                                                   | YES       |
| Database Settings    | DB_PORT             | -                                  | The port on which your SQL database runs                                            | Must be an integer between 1 and 65535                                            | YES       |
| Database Settings    | DB_NAME             | -                                  | The name of your database that you want to connect to                               |                                                                                   | YES       |
| Database Settings    | DB_PASSWD           | -                                  | The password of your SQL database                                                   |                                                                                   | YES       |
| Database Settings    | DB_USER             | -                                  | The user that the application will use when interacting with the db                 |                                                                                   | YES       |
| Database Settings    | DB_SSL              | True                               | Whether the connection between app and db should be established using SSL           |                                                                                   | NO        |
| Database Settings    | DB_ECHO             | True                               | Whether the backend should log its internal operations in the terminal              |                                                                                   | NO        |
| Database Settings    | DB_POOL_SIZE        | 20                                 | Number of database connections to maintain in the pool                              | Core concurrency limit for database operations                                    | NO        |
| Database Settings    | DB_MAX_OVERFLOW     | 30                                 | Additional connections allowed when pool is full                                    | Burst capacity for handling traffic spikes                                        | NO        |
| Database Settings    | DB_POOL_TIMEOUT     | 15                                 | Timeout in seconds waiting for available connection                                 | Prevents application from hanging on connection requests                          | NO        |
| Database Settings    | DB_POOL_RECYCLE     | 3600                               | Recycle connections after this many seconds                                         | Prevents stale connections in long-running applications                           | NO        |
| Performance Settings | THREAD_POOL         | 80                                 | The amount of threads that can be open concurrently for each worker                 | [More info](https://www.starlette.io/threadpool/)                                 | NO        |
| Performance Settings | WORKERS             | 4                                  | The amount of workers the uvicorn server uses                                       | Ideally this number is ~amount of CPU threads (not cores) for optimal scalability | NO        |

> [!Note]
> Variables are only mandatory if **no default value** exists.
