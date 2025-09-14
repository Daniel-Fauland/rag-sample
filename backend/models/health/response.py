from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="The status of the health check", examples=[
                        "healthy"])
    fastapi_version: str = Field(..., description="The version of the fastapi cli", examples=[
                                 "FastAPI CLI version: 0.0.8"])


class HealthCheckDBResponse(BaseModel):
    status: str = Field(..., description="The status of the health check", examples=[
                        "healthy"])
    current_database: str = Field(
        ..., description="The name of the currently active postgres database", examples=["backend"])
    current_user: str = Field(..., description="The name of the current database user", examples=[
                              "systemuser"])
