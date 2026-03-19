from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:password@localhost:5432/dse_dividends"
    dse_api_base_url: str = "https://data.dse.co.tz"
    secret_key: str = "change-me"
    sms_api_key: str = ""
    sms_username: str = ""
    whatsapp_token: str = ""
    whatsapp_verify_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_app_secret: str = ""
    allowed_origins: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"

    # Scraper settings
    dse_website_url: str = "https://www.dse.co.tz"
    scraper_timeout: int = 30
    scraper_max_retries: int = 3
    scraper_user_agent: str = "DSEDividendTracker/1.0"

    # Sync scheduling toggles
    sync_prices_enabled: bool = True
    sync_dividends_enabled: bool = True

    model_config = {"env_file": ".env"}


settings = Settings()
