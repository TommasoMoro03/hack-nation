from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Qui definisci le variabili che vuoi leggere dal file .env
    # Il nome della variabile deve corrispondere ESATTAMENTE a quello nel .env
    OPENAI_API_KEY: str

    # Questo dice a Pydantic di cercare un file chiamato ".env"
    model_config = SettingsConfigDict(env_file=".env")

# Creiamo un'istanza delle impostazioni che importeremo nel resto del codice
settings = Settings()