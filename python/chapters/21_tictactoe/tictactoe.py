#!/usr/bin/env python3
"""Tic-Tac-Toe: draw a board, maybe make one move, and say who has won."""

import argparse
import re

EMPTY = "."
LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
)


def winners(board: str) -> set[str]:
    """Every player with three in a row (a real game has at most one)."""
    return {board[a] for a, b, c in LINES if board[a] != EMPTY and board[a] == board[b] == board[c]}


def find_winner(board: str) -> str | None:
    """'X', 'O' or None."""
    found = winners(board)
    return found.pop() if len(found) == 1 else None


def problem(board: str) -> str | None:
    """Why a well-formed board can't come from a real game, or None if it can."""
    if len(winners(board)) > 1:
        return "both X and O have three in a row"
    if abs(board.count("X") - board.count("O")) > 1:
        return "players must take turns, so X and O counts differ by at most one"
    return None


def get_args() -> argparse.Namespace:
    """Parse and validate the command line."""
    parser = argparse.ArgumentParser(
        description="Tic-Tac-Toe",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-b", "--board", metavar="board", default=EMPTY * 9,
                        help="The state of the board")
    parser.add_argument("-p", "--player", choices="XO", default=None, help="Player")
    parser.add_argument("-c", "--cell", metavar="cell", type=int, default=None,
                        help="Cell 1-9")
    args = parser.parse_args()

    # Checked by hand, not with choices=: Python 3.12+ quotes the bad value ('10') and the
    # book's test expects the older, unquoted message.
    if args.cell is not None and not 1 <= args.cell <= 9:
        parser.error(f"argument -c/--cell: invalid choice: {args.cell} (choose from 1-9)")
    if not re.fullmatch(r"[.XO]{9}", args.board):
        parser.error(f'--board "{args.board}" must be 9 characters of ., X, O')
    if (args.player is None) != (args.cell is None):
        parser.error("Must provide both --player and --cell")
    trouble = problem(args.board)
    if trouble:
        parser.error(f'--board "{args.board}" is impossible: {trouble}')
    if args.cell is not None:
        if args.board[args.cell - 1] != EMPTY:
            parser.error(f'--cell "{args.cell}" already taken')
        if find_winner(args.board):
            parser.error(f"the game is over: {find_winner(args.board)} has already won")
    return args


def format_board(board: str) -> str:
    """The grid, with cell numbers where nobody has played."""
    rule = "-" * 13
    cells = [c if c != EMPTY else str(i) for i, c in enumerate(board, start=1)]
    rows = ["| " + " | ".join(cells[r:r + 3]) + " |" for r in (0, 3, 6)]
    return "\n".join([rule, rows[0], rule, rows[1], rule, rows[2], rule])


def main() -> None:
    """Draw the board after the move, then the verdict."""
    args = get_args()
    board = args.board
    if args.player:
        i = args.cell - 1
        board = board[:i] + args.player + board[i + 1:]
    print(format_board(board))
    winner = find_winner(board)
    print(f"{winner} has won!" if winner else "No winner.")


if __name__ == "__main__":
    main()
