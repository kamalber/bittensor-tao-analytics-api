import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_TOKEN: str = os.getenv("API_TOKEN", "default_token_for_development")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Redis Settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", "120"))  # Cache TTL in seconds
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/bittensor_api")
    
    # Bittensor Settings
    BITTENSOR_NETWORK: str = os.getenv("BITTENSOR_NETWORK", "testnet")
    DEFAULT_NETUID: int = int(os.getenv("DEFAULT_NETUID", "18"))
    DEFAULT_HOTKEY: str = os.getenv("DEFAULT_HOTKEY", "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v")
    WALLET_MNEMONIC: str = os.getenv("WALLET_MNEMONIC", "diamond like interest affair safe clarify lawsuit innocent beef van grief color")
    
    # External API Keys
    DATURA_API_KEY: str = os.getenv("DATURA_API_KEY", "dt_$q4qWC2K5mwT5BnNh0ZNF9MfeMDJenJ-pddsi_rE1FZ8")
    CHUTES_API_KEY: str = os.getenv("CHUTES_API_KEY", "cpk_9402c24cc755440b94f4b0931ebaa272.7a748b60e4a557f6957af9ce25778f49.8huXjHVlrSttzKuuY0yU2Fy4qEskr5J0")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()


