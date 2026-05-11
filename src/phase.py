import chess


def detect_phase(board: chess.Board) -> str:
    """Returns 'opening', 'middlegame', or 'endgame'."""
    # Count material
    piece_values = {
        chess.QUEEN: 9,
        chess.ROOK: 5,
        chess.BISHOP: 3,
        chess.KNIGHT: 3,
        chess.PAWN: 1,
    }

    total_material = 0
    non_pawn_material = 0
    has_queens = False

    for piece_type, value in piece_values.items():
        count = len(board.pieces(piece_type, chess.WHITE)) + len(board.pieces(piece_type, chess.BLACK))
        total_material += count * value
        if piece_type != chess.PAWN:
            non_pawn_material += count * value
        if piece_type == chess.QUEEN and count > 0:
            has_queens = True

    # Endgame: no queens, OR very little non-pawn material
    if not has_queens or non_pawn_material <= 20:
        return 'endgame'

    # Opening: early game with lots of material still on board
    if board.fullmove_number <= 12 and total_material >= 62:
        return 'opening'

    return 'middlegame'
