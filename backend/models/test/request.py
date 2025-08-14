from pydantic import BaseModel, Field, field_validator


class TestRequest(BaseModel):
    message: str = Field(..., description="The string to transform", examples=[
                         "This is a test sentence."])
    conversion_type: str = Field(..., examples=["upper"])

    @field_validator('conversion_type')
    @classmethod
    def validate_conversion_type(cls, v: str) -> str:
        valid_types = ["upper", "lower", "camelCase",
                       "PascalCase", "snake_case", "kebab-case"]
        if v.lower() not in [t.lower() for t in valid_types]:
            raise ValueError(f"conversion_type must be one of {valid_types}")
        # Return the normalized version (first matching case)
        for valid_type in valid_types:
            if v.lower() == valid_type.lower():
                return valid_type
        return v
