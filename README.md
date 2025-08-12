# RAG Sample

**Content Overview**

- [Feature Overview](#feature-overview)
- [Prerequisites](#prerequisites)
- [Run The Backend](#run-the-backend)
- [Run With Docker](#run-with-docker)
- [Env Variables Overview](#env-variables-overview)

## Feature Overview

This sample provides a FastAPI backend with the following features:

- [x] Using `uv` as a package manager.
- [x] Central [config.py](./backend/config.py) file for all env variables and settings.
- [x] Immediate validation of variables inside of [config.py](./backend/config.py) using `pydantic-settings`.
- [x] `Pydantic` models for api route request/response validation.
- [x] Global logging for the entire application. See [utils/logging.py](./backend/utils/logging.py).
- [x] Life span object with health check at startup for FastAPI app instance. See [main.py](./backend/main.py).
- [x] Middleware with execution timer for api routes. See [middleware.py](./backend/middleware.py).
- [x] Global API error setup using custom error classes. See [errors.py](./backend/errors.py).
- [x] Performance optimization (Customizable workers / customizable thread pool / faster event_loop with uvicorn[standard] / offloading of synchronous functions). See `.env` file.
- [x] Colored terminal output support with `termcolor`. See [helper.py](./backend/utils/helper.py)
- [] Integration tests.
- [x] Containerization of backend.

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

## Run The Backend

Make sure you have fulfilled all the prerequisites before proceeding. <br/>
In order to run a python project using `uv` simply run the following command in the backend directory:

```
uv run main.py
```

This will start the fastapi backend. It can be accessed in the browser by going to this url: [localhost:8000](http://localhost:8000/) <br/>
Swagger docs are available at: [localhost:8000/docs](http://localhost:8000/docs)

> [!Tip]
> If you want to link your vscode interpreter to the created venv for proper syntax highlighting follow these steps:
>
> 1. Run the backend at least once to create the `.venv` folder within the backend
> 2. Navigate to `backend/.venv/bin` and copy the path of the python binary
> 3. Open the VSC Command Palette CMD + SHIFT + P (or CTRL + SHIFT + P for Windows) and enter the option `Python: Select Interpreter`
> 4. Click on `Enter interpreter path...` and paste the python binary path

## Run With Docker

In order to use this application with docker make sure [docker](https://www.docker.com/) is installed and running.

### Docker backend

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

# Env Variables Overview

Here is an overview about the environment variables in your `.env` file:

| Category             | ENV Variable        | Default Value                      | Description                                                                         | Additional Information                                                            | Mandatory |
| -------------------- | ------------------- | ---------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | --------- |
| Basic Settings       | LOGGING_LEVEL       | INFO                               | The Logging level for the backend application                                       | Must be either DEBUG, INFO, WARNING, ERROR, CRITICAL                              | YES       |
| Basic Settings       | FASTAPI_WELCOME_MSG | Access the swagger docs at '/docs' | The default message shown when opening the fastapi url in the browser               |                                                                                   | YES       |
| Basic Settings       | FASTAPI_PORT        | 8000                               | The port at which the fastapi (uvicorn) backend runs                                |                                                                                   | YES       |
| Environment Settings | BACKEND_VERSION     | 0.0.1                              | The version of the fastapi backend                                                  | Must be in format x.y.z (e.g. 1.2.3)                                              | YES       |
| Environment Settings | IS_LOCAL            | False                              | Whether the backend runs on a local machine or somewhere else (e.g. Cloud instance) |                                                                                   | YES       |
| Environment Settings | IS_DOCKER           | True                               | Whether the backend runs within a docker container                                  |                                                                                   | YES       |
| Performance Settings | THREAD_POOL         | 80                                 | The amount of threads that can be open concurrently for each worker                 | [More info](https://www.starlette.io/threadpool/)                                 | YES       |
| Performance Settings | WORKERS             | 4                                  | The amount of workers the uvicorn server uses                                       | Ideally this number is ~amount of CPU threads (not cores) for optimal scalability | YES       |

> [!Note]
> Mandatory variables must **only be** explicitly **set** if they have **no default value**. Otherwise the default value will be chosen automatically.
