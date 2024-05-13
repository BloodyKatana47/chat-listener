import json
from typing import Dict, List

from models import Account, Settings

settings: Settings = Settings(_env_file='.env')


def load_accounts_configs() -> Dict[str, List[Account]]:
    """
    Loads accounts from accounts.json file.
    """
    with open('accounts.json') as file:
        data: Dict[str, List[Account]] = json.load(file)['accounts']
    return data
