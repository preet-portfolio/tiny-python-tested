#!/usr/bin/env python3
"""Interactive Tic-Tac-Toe, a first try: one game object that each move updates."""

from dataclasses import dataclass

WINS = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))


@dataclass
class State:
    """The game. Each move writes straight into it."""

    board: str = "." * 9
    player: str = "X"
    quit: bool = False
    draw: bool = False
    error: str | None = None
    winner: str | None = None


def format_board(board: str) -> str:
    """The grid, with numbers in the empty cells."""
    cells = [str(i + 1) if c == "." else c for i, c in enumerate(board)]
    bar = "-------------"
    rows = [f"| {cells[r]} | {cells[r + 1]} | {cells[r + 2]} |" for r in (0, 3, 6)]
    return "\n".join([bar, rows[0], bar, rows[1], bar, rows[2], bar])


def find_winner(board: str) -> str | None:
    """'X' or 'O' with three in a row, else None."""
    for player in "XO":
        for a, b, c in WINS:
            if board[a] == board[b] == board[c] == player:
                return player
    return None


def get_move(state: State, text: str) -> State:
    """Apply one move to the game."""
    state.error = None
    if text.strip().lower() == "q":
        state.quit = True
        return state
    if text.strip() not in list("123456789"):
        state.error = f'Invalid cell "{text.strip()}", please use 1-9'
        return state
    cell = int(text) - 1
    if state.board[cell] != ".":
        state.error = f'Cell "{text.strip()}" already taken'
        return state
    state.board = state.board[:cell] + state.player + state.board[cell + 1 :]
    if "." not in state.board:
        state.draw = True
    else:
        state.winner = find_winner(state.board)
    state.player = "O" if state.player == "X" else "X"
    return state


def main() -> None:
    """Play until there's a winner, a draw or a quit."""
    state = State()
    while True:
        print(format_board(state.board))
        if state.error:
            print(state.error)
        if state.winner:
            print(f"{state.winner} has won!")
            break
        if state.draw:
            print("All right, we'll call it a draw.")
            break
        if state.quit:
            print("You quit. Bye!")
            break
        state = get_move(state, input(f"Player {state.player}, what is your move? [q to quit]: "))


if __name__ == "__main__":
    main()
