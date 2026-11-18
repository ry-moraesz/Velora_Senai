from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file='../.env',extra='ignore')
    database_url:str='postgresql+psycopg://velora:velora_dev@localhost:5432/velora'
    jwt_secret:str='development-only-change-this-secret-before-deploying'
    access_token_minutes:int=30
    cors_origins:str='http://localhost:5173'
settings=Settings()
