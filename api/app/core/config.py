"""Application Configuration via Pydantic Settings."""

import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # App Info
    APP_NAME: str = "SIFT - Safety Intelligence & Fatality-risk Tracking"
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Server Binding
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://192.168.1.100:5174",
        "http://localhost:5174",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./sift.db"
    DB_ECHO: bool = False
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "sift_dev"

    # Security
    SECRET_KEY: str = "sift-super-secret-key-change-in-production-2026-oil-india"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # AI & NLP Layer
    AI_PROVIDER: str = "mock"  # mock, gemini, huggingface, openai
    AI_CONFIDENCE_THRESHOLD: int = 85
    AI_MODEL_NAME: str = "sift-nlp-precursor-v2.4"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Vector Storage Layer
    VECTOR_STORE_PROVIDER: str = "mock"  # mock, pinecone
    EMBEDDING_PROVIDER: str = "mock"     # mock, openai, hf
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX_NAME: str = "sift-safety-reports"
    PINECONE_DIMENSION: int = 1536


settings = Settings()
