from ..abstract_interface.interface import Interface
from .cli_commands import (
    ShutDownCommand,
    help,
    save,
    history,
    next,
    state,
    delete_save
)
import os.path


def command_line_interface():
    print("Do you want to start a new game, or continue a previous one?")
    print("0 - new game")
    print("1 - load a save file")
    answer = input("Your choice: ").strip()
    while answer not in {'0', '1'}:
        print("Invalid choice")
        answer = input("Your choice: ").strip()

    if answer == '0':
        dirname = "starting"
    else:
        dirname = input("Enter the name of the save: ").strip()
        while not os.path.isfile("saves/" + dirname + "/history.txt"):
            print("Invalid save name")
            dirname = input("Enter the name of the save: ").strip()
    print("Loading saves/" + dirname)
    interface = Interface()
    interface.load_data(dirname)

    while True:
        try:
            print("Enter a command. Enter help for a list of commands.")
            answer = input().strip().split(' ')
            if answer[0] == "help":
                help()
            elif answer[0] in {"save", "sv"}:
                save(answer, interface)
            elif answer[0] in {"exit", "e"}:
                raise ShutDownCommand
            elif answer[0] in {"history", "h"}:
                history(answer, interface)
            elif answer[0] in {"next", "n"}:
                next(answer, interface)
            elif answer[0] in {"state", "s"}:
                state(answer, interface)
            elif answer[0] in {"del", "d"}:
                delete_save(answer)
            else:
                print("Invalid command. Enter help for a list of commands.")
        except ShutDownCommand:
            print("Shutting down")
            return
