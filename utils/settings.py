from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()


class Settings:
    USE_PROXY: bool = bool(os.getenv("USE_PROXY", True))
    PROXY_TYPE: str = str(os.getenv("PROXY_TYPE", "socks4"))

    WORKDIR = os.getenv("WORKDIR", "sessions/")

    # Email Configuration
    MAIL_HOST: str = os.getenv("MAIL_HOST", "smtp.gmail.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 465))
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "gmail@gmail.com")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "password")
    MAIL_FROM_ADDRESS: str = os.getenv("MAIL_FROM_ADDRESS", "gmail@gmail.com")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "APP_NAME")

    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str | int = os.getenv("DB_PORT", 3306)
    DB_DATABASE: str = os.getenv("DB_DATABASE", "database_name")
    DB_USERNAME: str = os.getenv("DB_USERNAME", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    class Config:
        env_file = ".env"


settings = Settings()
