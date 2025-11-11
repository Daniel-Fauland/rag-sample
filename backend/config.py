import re
from pydantic import Field, field_validator, ValidationError
from pydantic_settings import SettingsConfigDict, BaseSettings
from utils.config_helper import helper

# Quick access to color coding function
color = helper.config_color


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # --- Basic Settings ---
    logging_level: str = Field(
        default="INFO",
        description="Logging level for the application"
    )

    fastapi_welcome_msg: str = Field(
        default="Access the swagger docs at '/docs'",
        description="The default message shown when opening the fastapi url in the browser"
    )

    fastapi_port: int = Field(
        default=8000,
        description="The port at which the fastapi (uvicorn) backend runs"
    )

    # --- Environment Settings ---
    backend_version: str = Field(
        default="0.0.1",
        description="The version of the fastapi backend"
    )

    is_local: bool = Field(
        default=False,
        description="Wheter the backend runs on a local machine or somewhere else (e.g. Cloud instance)"
    )

    is_docker: bool = Field(
        default=True,
        description="Wheter the backend runs within a docker container"
    )

    # --- Performance Settings ---
    thread_pool: int = Field(
        default=80,
        description="The amount of threads that can be open concurrently for each worker"
    )

    workers: int = Field(
        default=4,
        description="The amount of workers the uvicorn server uses."
    )

    # --- Test Settings ---
    test_logging_level: str = Field(
        default="WARNING",
        description="Logging level for the application"
    )

    # --- Validation methods ---
    @field_validator("logging_level", "test_logging_level")
    @classmethod
    def validate_logging_level(cls, v: str) -> str:
        """Validate logging level is a valid Python logging level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        level = v.upper()
        if level not in valid_levels:
            raise ValueError(
                f"invalid logging level {color(v)}. Must be one of: {color(', '.join(valid_levels))}"
            )
        return level

    @field_validator("backend_version")
    @classmethod
    def validate_backend_version(cls, v: str) -> str:
        """Validate backend version is a valid version string."""
        # if not v:
        #     raise ValueError("backend version is required")
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError(
                f"invalid version format {color(v)}. Must be in the format: {color("x.y.z (e.g. 1.2.3)")}")
        return v

    def validate_all(self) -> None:
        """Validate all settings and raise ValidationError if any fail."""
        # This method is automatically called by Pydantic
        pass


# Map variables names to .env variable names
# This is OPTIONAL UNLESS the variable name differs from .env variable name (case in-sensitive)
field_mapping = {
    "logging_level": "LOGGING_LEVEL",
    "backend_version": "BACKEND_VERSION"
}

# Create and validate config instance
try:
    config = Settings()
except ValidationError as e:
    helper.validation_handler(error=e, field_mapping=field_mapping)
except Exception as e:
    helper.exception_handler(error=e)
