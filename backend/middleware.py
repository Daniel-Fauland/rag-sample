import time
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from utils.helper import color
from utils.logging import logger


def register_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"])

    @app.middleware('http')
    async def execution_timer(request: Request, call_next):
        """This execution timer is an example how middleware can be used."""
        start_time = time.perf_counter()
        response = await call_next(request)
        processing_time = round(time.perf_counter() - start_time, 3)
        prefix = f"{request.method} {request.url.path}"
        logger.info(
            f"{await color(prefix)} completed after: {await color(str(processing_time) + "s")}")
        return response
