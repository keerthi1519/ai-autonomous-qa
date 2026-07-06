from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GROQ_API_KEY: str

    # Default must be a model Groq actually hosts,
    # since ai_client.py points at the Groq API.
    MODEL_NAME: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
