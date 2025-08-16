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
- [Postgres Database Setup](#postgres-database-setup)
  - [Local Postgres DB](#local-postgres-db)
  - [Online Postgres DB](#online-postgres-db)
- [Run The Backend locally](#run-the-backend-locally)
- [Run The Backend With Docker](#run-the-backend-with-docker)
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
- [ ] Postgres db integration.

> TODO: Alembic Migrations <br/>
> TODO: DB Schemas using SQLModel <br/>
> TODO: Dummy data ingestions <br/>
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

## Postgres Database Setup

### Local Postgres DB

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
   ```

   > [!Note]
   > If you change these default values make sure to also adjust the `.env` file to ensure correct credentials for the backend application.

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
   docker run --name ${PG_CONTAINER} --network ${PG_NETWORK_NAME} -p 5432:5432 -e POSTGRES_PASSWORD=${PG_PASSWORD} -e POSTGRES_DB=${PG_NAME} -e POSTGRES_USER=${PG_USER} -d postgres:${PG_VERSION}
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
   > You can stop and remove the running postgres container with this command: <br/> > `docker stop ${PG_CONTAINER} && docker rm ${PG_CONTAINER}`

   > [!Tip]
   > You can now also connect to this database through any UI based database program like [pgAdmin](https://www.pgadmin.org) when providing the following credentials: <br/>
   > Host name/address: `localhost` <br/>
   > Port: `5432` <br/>
   > Maintenance database: The value of: `${PG_NAME}` <br/>
   > Username: The value of: `${PG_USER}` <br/>
   > Password: The value of: `${PG_PASSWORD}`

### Online Postgres DB

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

## Run The Backend Locally

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

## Run The Backend With Docker

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
| Performance Settings | THREAD_POOL         | 80                                 | The amount of threads that can be open concurrently for each worker                 | [More info](https://www.starlette.io/threadpool/)                                 | NO        |
| Performance Settings | WORKERS             | 4                                  | The amount of workers the uvicorn server uses                                       | Ideally this number is ~amount of CPU threads (not cores) for optimal scalability | NO        |

> [!Note]
> Variables are only mandatory if **no default value** exists.
