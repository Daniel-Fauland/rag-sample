import re
from pydantic import Field, field_validator, ValidationError
from pydantic_settings import SettingsConfigDict, BaseSettings
from functools import cached_property
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

    fastapi_project_name: str = Field(
        default="FastAPI",
        description="The Project of you application used in the Swagger title"
    )

    fastapi_welcome_msg: str = Field(
        default="Access the swagger docs at '/docs'",
        description="The default message shown when opening the fastapi url in the browser"
    )

    fastapi_port: int = Field(
        default=8000,
        description="The port at which the fastapi (uvicorn) backend runs"
    )

    rate_limit_unprotected_routes: str = Field(
        default="10",
        description="How many requests a client (ip address) can make against the same API route per minute on unprotected routes"
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

    # --- User Settings ---
    default_user_role: str = Field(
        default="user",
        description="The default role that is assigned at user creation. Can only assign roles that exist in the db."
    )

    # --- Database Settings ---
    db_host: str = Field(
        description="The host name of your sql database"
    )

    db_port: int = Field(
        description="The Port on which your sql database runs"
    )

    db_name: str = Field(
        description="The name of your database that you want to connect to"
    )

    db_passwd: str = Field(
        description="The password of your sql database"
    )

    db_user: str = Field(
        description="The user that the application will use when interacting with the db"
    )

    db_ssl: bool = Field(
        default=True,
        description="Wheter the connection between app and db should be established using ssl"
    )

    db_echo: bool = Field(
        default=True,
        description="Whether the backend should log its internal operations in the terminal"
    )

    db_pool_size: int = Field(
        default=20,
        description="Number of database connections to maintain in the pool"
    )

    db_max_overflow: int = Field(
        default=30,
        description="Additional connections allowed when pool is full"
    )

    db_pool_timeout: int = Field(
        default=15,
        description="Timeout in seconds waiting for available connection"
    )

    db_pool_recycle: int = Field(
        default=3600,
        description="Recycle connections after this many seconds"
    )

    # --- Redis Settings ---
    redis_host: str = Field(
        description="The host name of your redis database"
    )
    redis_port: int = Field(
        description="The port on which your redis database runs"
    )

    redis_password: str = Field(
        description="The password of your redis database"
    )

    redis_ssl: bool = Field(
        default=True,
        description="hWheter the connection between app and db sould be established using ssl"
    )

    redis_pool_size: int = Field(
        default=20,
        description="Number of database connections to maintain in the pool"
    )

    @cached_property
    def db_uri(self) -> str:
        """Construct the database URI from individual components."""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_passwd}@{self.db_host}:{self.db_port}/{self.db_name}"

    # --- JWT Settings ---
    jwt_algorithm: str = Field(
        default="HS256",
        description="The JWT algorithm used for signing and verifying JWTs"
    )

    jwt_secret: str = Field(
        description="The JWT secret key used for de-/encoding JWTs"
    )

    jwt_access_token_expiry: int = Field(
        description="The life span of a generated access token in minutes",
        default=15
    )

    jwt_refresh_token_expiry: int = Field(
        description="The life span of a generated refresh token in days",
        default=30
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
        default="ERROR",
        description="Logging level for the application"
    )

    test_db_name: str = Field(
        default="pg_test_db",
        description="The name of your test database that you want to connect to"
    )

    # --- Validation methods ---
    # - Validation of Basic Settings-
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

    @field_validator("rate_limit_unprotected_routes")
    @classmethod
    def validate_rate_limit_unprotected_routes(cls, v: str) -> str:
        """Validate rate_limit_unprotected_routes is a valid number > 0."""
        try:
            int_v = int(v)
            if int_v < 1:
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError(
                f"invalid rate limit {color(v)}. Must be a valid integer > 0."
            )
        return v

    # - Validation of Environment Settings -
    @field_validator("backend_version")
    @classmethod
    def validate_backend_version(cls, v: str) -> str:
        """Validate backend version is a valid version string."""
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError(
                f"invalid version format {color(v)}. Must be in the format: {color("x.y.z (e.g. 1.2.3)")}")
        return v

    # - Validation of Database Settings -
    @field_validator("db_port", "redis_port")
    @classmethod
    def validate_db_port(cls, v: int) -> int:
        """Validate database port is a valid port number."""
        if not isinstance(v, int) or v < 1 or v > 65535:
            raise ValueError(
                f"invalid port number {color(v)}. Must be an integer between 1 and 65535"
            )
        return v

    # - Validation of JWT Settings -
    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT secret is at least 256 bits (32 bytes) long."""
        # Convert to bytes to check length
        secret_bytes = v.encode('utf-8')
        min_bits = 256
        min_bytes = min_bits // 8  # 32 bytes

        if len(secret_bytes) < min_bytes:
            raise ValueError(
                f"JWT secret must be at least {color(str(min_bits))} bits ({color(str(min_bytes))} bytes) long. "
                f"Current length: {color(str(len(secret_bytes) * 8))} bits ({color(str(len(secret_bytes)))} bytes)"
            )
        return v

    @field_validator("jwt_access_token_expiry")
    @classmethod
    def validate_jwt_access_token_expiry(cls, v: int) -> int:
        """Validate if token expiry is valid"""
        if not isinstance(v, int) or v < 1 or v > 999:
            raise ValueError(
                f"invalid access token expiry {color(v)}. Must be an integer between 1 and 999"
            )
        return v

    @field_validator("jwt_refresh_token_expiry")
    @classmethod
    def validate_jwt_refresh_token_expiry(cls, v: int) -> int:
        """Validate if token expiry is valid"""
        if not isinstance(v, int) or v < 1 or v > 999:
            raise ValueError(
                f"invalid access token expiry {color(v)}. Must be an integer between 1 and 999"
            )
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
