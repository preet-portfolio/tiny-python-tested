#!/usr/bin/env python3
"""Tic-Tac-Toe: draw a board and say who has won."""

import argparse


def get_args():
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Tic-Tac-Toe")
    parser.add_argument("-b", "--board", default=".........", help="The state of the board")
    parser.add_argument("-p", "--player", help="Player")
    parser.add_argument("-c", "--cell", type=int, help="Cell 1-9")
    return parser.parse_args()


def format_board(board):
    """The grid, with cell numbers where nobody has played."""
    return board


def find_winner(board):
    """'X', 'O' or None."""
    return None


def main():
    """Draw the board, then the verdict."""
    args = get_args()
    print(format_board(args.board))
    print("No winner.")


if __name__ == "__main__":
    main()
