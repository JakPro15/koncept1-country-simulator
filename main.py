from sources.cli.cli import command_line_interface
from sys import argv
import argparse


def main(arguments):
    parser = argparse.ArgumentParser(
        prog='Koncept 1 - main.py',
        description='Game/simulation of a pre-industrial country.'
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-c', '--cli', action='store_true', help='whether to '
                      'launch the program in the command line')
    mode.add_argument('-g', '--gui', action='store_true', help='whether to '
                      'launch the program with graphical user interface')
    parser.add_argument('-d', '--debug', action='store_true', help='whether '
                        'to print debug information to standard output')
    args = parser.parse_args(arguments[1:])

    if args.gui:
        raise NotImplementedError(
            "Graphical user interface has not been implemented yet."
        )
    elif args.cli:
        command_line_interface(args.debug)


if __name__ == "__main__":
    main(argv)
