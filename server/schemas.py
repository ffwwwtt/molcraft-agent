"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, EmailStr, Field


# ── Auth ──

class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    display_name: str = Field(default="", max_length=100)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Config ──

class ConfigUpdate(BaseModel):
    api_key: str = Field(default="", max_length=512)
    base_url: str = Field(default="", max_length=500)
    model: str = Field(default="", max_length=200)
    temperature: float = Field(default=0.3, ge=0, le=2.0)
    max_iterations: int = Field(default=3, ge=1, le=20)
    max_minutes: int = Field(default=90, ge=5, le=480)
    system_prompt: str = Field(default="", max_length=10000)
    write_paper: bool = Field(default=False)


# ── Agent ──

class AgentStartRequest(BaseModel):
    goal: str = Field(..., min_length=1, max_length=5000)
    conv_id: str | None = None
    write_paper: bool = False
    max_iterations: int = Field(default=3, ge=1, le=20)
    max_minutes: int = Field(default=90, ge=5, le=480)
    system_prompt: str = Field(default="", max_length=10000)


# ── Conversation ──

class ConversationCreate(BaseModel):
    title: str = Field(default="Untitled Research", max_length=500)
    goal: str = Field(default="", max_length=5000)


class ConversationUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    goal: str | None = None
    config: dict | None = None
