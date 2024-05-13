import json
from typing import Dict, List

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    admin_username: str
    database_name: str = 'users.db'
    folder_name: str = 'downloads'


settings: Settings = Settings(_env_file='.env')


class Account(BaseModel):
    api_hash: str
    api_id: int
    session_name: str


def load_accounts_configs() -> Dict[str, List[Account]]:
    """
    Loads accounts from accounts.json file.
    """
    with open('accounts.json') as file:
        data: Dict[str, List[Account]] = json.load(file)
    return data
