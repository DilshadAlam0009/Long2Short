from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    HUGGINGFACE_MODEL: str

    CHROMA_PATH: str = "./data/chroma"
    UPLOAD_PATH: str = "./data/uploads"

    class Config:
        env_file = ".env"


settings = Settings()