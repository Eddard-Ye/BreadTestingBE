import unicodedata

from pydantic import AliasChoices, BaseModel, Field, field_validator


def normalize_password(value: str) -> str:
    return unicodedata.normalize("NFKC", value.strip())


class LoginRequest(BaseModel):
    password: str = Field(
        min_length=1,
        validation_alias=AliasChoices("password", "passcode"),
    )

    @field_validator("password")
    @classmethod
    def normalize(cls, value: str) -> str:
        normalized = normalize_password(value)
        if not normalized:
            raise ValueError("password must not be empty")
        return normalized


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
