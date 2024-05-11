from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_hash: str
    api_id: int
    admin_id: int
    database_name: str = 'users.db'
    session_name: str = 'my_account'
    folder_name: str = 'downloads'


settings: Settings = Settings(_env_file=".env")
