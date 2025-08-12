from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="The status of the health check", examples=[
                        "healthy"])
    fastapi_version: str = Field(..., description="The version of the fastapi cli", examples=[
                                 "FastAPI CLI version: 0.0.8"])
