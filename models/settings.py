from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    admin_username: str
    database_name: str = 'users.db'
    files_folder_name: str = 'downloads'
    sessions_folder_name: str = 'sessions'
