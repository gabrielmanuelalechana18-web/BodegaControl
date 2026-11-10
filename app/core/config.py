import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "BodegaControl - Bodega 'Chanita'"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bodegacontrol_local.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_change_in_prod")
    MAX_CREDIT_LIMIT: float = float(os.getenv("MAX_CREDIT_LIMIT_DEFAULT", 100.00))
    MAX_OVERDUE_DAYS: int = int(os.getenv("MAX_OVERDUE_DAYS", 30))
    MIN_PROFIT_MARGIN: float = float(os.getenv("MIN_PROFIT_MARGIN", 0.20))

settings = Settings()
