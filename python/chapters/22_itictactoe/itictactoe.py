#!/usr/bin/env python3
"""Interactive Tic-Tac-Toe: two players take turns at the keyboard until someone wins."""

import re
from typing import NamedTuple

WINS = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))


class State(NamedTuple):
    """Everything about the game at one moment. A move makes a new State; none is changed."""

    board: str = "." * 9
    player: str = "X"
    quit: bool = False
    draw: bool = False
    error: str | None = None
    winner: str | None = None

    @property
    def over(self) -> bool:
        """True once someone has won, it's a draw, or a player quit."""
        return bool(self.winner or self.draw or self.quit)


def format_board(board: str) -> str:
    """The grid, with the cell's number wherever nobody has played."""
    cells = [str(i + 1) if c == "." else c for i, c in enumerate(board)]
    bar = "-------------"
    rows = [f"| {cells[r]} | {cells[r + 1]} | {cells[r + 2]} |" for r in (0, 3, 6)]
    return "\n".join([bar, rows[0], bar, rows[1], bar, rows[2], bar])


def find_winner(board: str) -> str | None:
    """'X' or 'O' if they have three in a row, else None."""
    for player in "XO":
        if any(all(board[i] == player for i in line) for line in WINS):
            return player
    return None


def get_move(state: State, text: str) -> State:
    """The game after ``state.player`` types ``text``. A finished game ignores moves."""
    if state.over:
        return state
    move = text.strip()
    if move.lower() == "q":
        return state._replace(quit=True, error=None)
    if not re.fullmatch("[1-9]", move):
        return state._replace(error=f'Invalid cell "{move}", please use 1-9')
    cell = int(move) - 1
    if state.board[cell] != ".":
        return state._replace(error=f'Cell "{move}" already taken')
    board = state.board[:cell] + state.player + state.board[cell + 1 :]
    winner = find_winner(board)
    return State(
        board=board,
        player="O" if state.player == "X" else "X",
        draw=winner is None and "." not in board,
        winner=winner,
    )


def main() -> None:
    """Play until there's a winner, a draw, a quit, or the keyboard runs out of moves."""
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
        try:
            text = input(f"Player {state.player}, what is your move? [q to quit]: ")
        except EOFError:
            print("\nNo more moves. Bye!")
            break
        state = get_move(state, text)


if __name__ == "__main__":
    main()
