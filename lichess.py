
from functools import cached_property
import os
from typing import Generator
import berserk
from berserk.types.account import AccountInformation


class LiChessClient:
    def __init__(self):
        session = berserk.TokenSession(os.environ["LICHESS_API_TOKEN"])
        self.client = berserk.Client(session=session)

    @cached_property
    def username(self) -> str:
        return self.account['username']


    @cached_property
    def account(self) -> AccountInformation:
        return self.client.account.get()

    def games(self) -> Generator:
        yield from self.client.games.export_by_player(self.username)
