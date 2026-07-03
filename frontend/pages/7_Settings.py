from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# ---------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):

    # ---------------------------------------------------
    # AI Configuration
    # ---------------------------------------------------

    GROQ_API_KEY: str

    MODEL_NAME: str = "llama-3.3-70b-versatile"

    # ---------------------------------------------------
    # Application
    # ---------------------------------------------------

    APP_NAME: str = "AI Autonomous QA Engineer"

    APP_VERSION: str = "1.0.0"

    DEBUG: bool = True

    # ---------------------------------------------------
    # Directories
    # ---------------------------------------------------

    UPLOAD_FOLDER: str = "uploads"

    GENERATED_TESTS_FOLDER: str = "generated_tests"

    REPORTS_FOLDER: str = "reports"

    PROMPTS_FOLDER: str = "app/prompts"

    # ---------------------------------------------------
    # Selenium
    # ---------------------------------------------------

    CHROME_HEADLESS: bool = True

    SELENIUM_TIMEOUT: int = 20

    # ---------------------------------------------------
    # API
    # ---------------------------------------------------

    API_PREFIX: str = ""

    class Config:

        env_file = ".env"

        extra = "ignore"


settings = Settings()