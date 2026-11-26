#!/usr/bin/env python3
"""Interactive Tic-Tac-Toe: two players take turns at the keyboard."""

from typing import NamedTuple


class State(NamedTuple):
    """Everything about the game at one moment."""

    board: str = "." * 9
    player: str = "X"
    quit: bool = False
    draw: bool = False
    error: str | None = None
    winner: str | None = None


def format_board(board):
    """The grid, with the cell's number wherever nobody has played."""
    return board


def find_winner(board):
    """'X' or 'O' if they have three in a row, else None."""
    return None


def get_move(state, text):
    """The game after state.player types text."""
    return state


def main():
    """Play until the game is over."""
    state = State()
    print(format_board(state.board))


if __name__ == "__main__":
    main()
