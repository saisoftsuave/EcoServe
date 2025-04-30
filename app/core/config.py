from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    HOST: str
    DATABASE_URL: str
    DATABASE_URL_DOCKER: str
    TEST_DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    INVITE_TOKEN_EXPIRE_TIME: int
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    ALGORITHM: str
    SMTP_SERVER: str
    SMTP_PORT: int
    EMAIL_ADDRESS: str
    EMAIL_PASSWORD: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_REGION: str
    S3_BUCKET_NAME: str
    S3_FOLDER_NAME: str
    STRIPE_WEBHOOK_SECRET:str
    STRIPE_API_KEY:str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()
