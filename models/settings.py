from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    admin_username: str
    database_name: str = 'users.db'
    folder_name: str = 'downloads'
