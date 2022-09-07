from sources.cli.cli import command_line_interface
from sources.gui.gui import graphical_user_interface
from sys import argv
import argparse


def main(arguments: list[str]):
    parser = argparse.ArgumentParser(
        prog='Koncept 1 - main.py',
        description='Game/simulation of a pre-industrial country.'
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-c', '--cli', action='store_true', help='whether to '
                      'launch the program in the command line')
    mode.add_argument('-g', '--gui', action='store_true', help='whether to '
                      'launch the program with graphical user interface')
    parser.add_argument('-l', '--load', help='name of the save from which to '
                        'load game state; not given means a new game is '
                        'started', nargs=1, type=str, default=['starting'])
    args = parser.parse_args(arguments[1:])

    if args.gui:
        graphical_user_interface(args.load[0])
    elif args.cli:
        command_line_interface(args.load[0])


if __name__ == "__main__":
    main(argv)
