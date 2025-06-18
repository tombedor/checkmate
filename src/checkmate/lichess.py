
from functools import cached_property
import os
from typing import Generator, Dict, Any
import datetime
import berserk
from berserk.types.account import AccountInformation
from litellm import completion
from litellm.files.main import ModelResponse


def convert_to_pgn(game: Dict[str, Any]) -> str:
    """
    Convert a game in Lichess API JSON format to standard PGN format.

    Args:
        game: A dictionary containing game data from the Lichess API

    Returns:
        A string containing the game in PGN format
    """
    # Extract metadata for PGN headers
    game_id = game.get('id', '')
    white_player = game.get('players', {}).get('white', {}).get('user', {}).get('name', 'Unknown')
    black_player = game.get('players', {}).get('black', {}).get('user', {}).get('name', 'Unknown')
    white_elo = game.get('players', {}).get('white', {}).get('rating', '?')
    black_elo = game.get('players', {}).get('black', {}).get('rating', '?')
    result = '1-0' if game.get('winner') == 'white' else ('0-1' if game.get('winner') == 'black' else '1/2-1/2')

    # Format the date
    created_at = game.get('createdAt')
    date_str = created_at.strftime('%Y.%m.%d') if isinstance(created_at, datetime.datetime) else '????.??.??'

    # Get time control
    initial = game.get('clock', {}).get('initial', 0)
    increment = game.get('clock', {}).get('increment', 0)
    time_control = f"{initial}+{increment}"

    # Get variant
    variant = game.get('variant', 'standard')

    # Get termination
    status = game.get('status', 'unknown')
    termination = f"{status.capitalize()}"

    # Build PGN headers
    pgn = f"""[Event "Lichess {game.get('speed', 'game')}"]
[Site "https://lichess.org/{game_id}"]
[Date "{date_str}"]
[Round "?"]
[White "{white_player}"]
[Black "{black_player}"]
[Result "{result}"]
[WhiteElo "{white_elo}"]
[BlackElo "{black_elo}"]
[TimeControl "{time_control}"]
[Variant "{variant}"]
[Termination "{termination}"]

"""

    # Format moves
    moves_str = game.get('moves', '')
    moves_list = moves_str.split()

    # Group moves in pairs with move numbers
    formatted_moves = []
    for i in range(0, len(moves_list), 2):
        move_num = i // 2 + 1
        white_move = moves_list[i] if i < len(moves_list) else ""

        if i + 1 < len(moves_list):
            black_move = moves_list[i + 1]
            formatted_moves.append(f"{move_num}. {white_move} {black_move}")
        else:
            formatted_moves.append(f"{move_num}. {white_move}")

    # Add moves to PGN
    pgn += " ".join(formatted_moves)

    # Add result at the end
    pgn += f" {result}"

    return pgn


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

    @property
    def games(self) -> Generator:
        for game in self.client.games.export_by_player(self.username):
            yield game

    def get_pgn_games(self) -> Generator[str, None, None]:
        """
        Get games in PGN format.

        Returns:
            A generator yielding games in PGN format
        """
        for game in self.games:
            yield convert_to_pgn(game)



class AiClient:
    def __init__(self, model: str = "gpt-4o"):
        self.model = model

    def analyze(self, pgn_game: str) -> str:
        response = completion(

            self.model,
            messages = [
                {"role": "system", "content": "You are a chess tutor. Given a PGN annotated chess match, your job is to add annotations and commentary for what the user could learn to improve on, and what they did well. Your response should be in valid pgn format."},
                {"role": "user", "content": pgn_game}
            ],
            stream=False,
        )

        assert isinstance(response, ModelResponse)

        return response.choices[0].message.content # type: ignore


if __name__ == "__main__":
    client = LiChessClient()
    g = convert_to_pgn(next(client.games))


    print(AiClient().analyze(g))

