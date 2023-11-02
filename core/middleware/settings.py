from environs import Env
from dataclasses import dataclass


@dataclass
class Bots:
    token: str
    admin_id: str

@dataclass
class Settings:
    bots: Bots


def get_settings(path: str):
    env = Env()
    env.read_env(path)
    return Settings(
        bots=Bots(
            token=env.str("TOKEN"),
            admin_id=env.str("ADMIN_ID")
        )
    )

settings = get_settings('input')
print(settings.bots.token)