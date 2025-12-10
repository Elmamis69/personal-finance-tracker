from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "Personal Finance Tracker"
    env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # MongoDB
    mongodb_url: str
    mongodb_db_name: str

    # InfluxDB
    influxdb_url: str
    influxdb_token: str
    influxdb_org: str
    influxdb_bucket: str

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        case_sensitive = False
    )

# Global settings instance
settings = Settings()