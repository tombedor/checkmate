# Using rich console,
# render a chess board, in which arrow presses advance the board
from typing import List
from pydantic import BaseModel


class Commentary(BaseModel):
    moves: List[str]
    comment: str

class AnnotatedChessGame(BaseModel):
    moves: List[str]
    commentary: List[Commentary]
    summary: str







