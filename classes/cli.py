from .interface import Interface
from .cli_commands import (
    help,
    save,
    history,
    next,
    state
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
    print("Loading " + "saves/" + dirname)
    interface = Interface()
    interface.load_data(dirname)

    while True:
        print("Enter a command. Enter help for a list of commands.")
        answer = input().strip().split(' ')
        if answer[0] == "help":
            help()
        elif answer[0] == "save":
            save(answer, interface)
        elif answer[0] == "exit":
            print("Shutting down")
            return
        elif answer[0] == "history":
            history(answer, interface)
        elif answer[0] == "next":
            next(answer, interface)
        elif answer[0] == "state":
            state(answer, interface)
        else:
            print("Invalid command. Enter help for a list of commands.")
