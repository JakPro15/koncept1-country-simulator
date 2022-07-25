from ..abstract_interface.interface import (
    Interface,
    MalformedSaveError,
    SaveAccessError
)
from .cli_commands import (
    ShutDownCommand,
    fill_command,
    help,
    save,
    history,
    next,
    state,
    delete_save,
    exit_game
)
from .cli_game_commands import (
    transfer,
    secure,
    optimal,
    laws,
    promote,
    recruit,
    fight
)
import traceback


def command_line_interface(dirname):
    try:
        print("Loading saves/" + dirname)
        interface = Interface()
        try:
            interface.load_data(dirname)
        except SaveAccessError:
            print("Failed to open the save file. Shutting down.")
            return
        except MalformedSaveError:
            print("The program encountered an error while loading the save"
                  " file. Probably the file format is invalid. Shutting down.")
            return

        while True:
            try:
                print("Enter a command. Enter help for a list of commands.")
                execute(input().strip(), interface)
            except ShutDownCommand:
                print("Shutting down.")
                return
    except BaseException:
        print("An unexpected exception has occurred and the program will"
              " be terminated.")
        traceback.print_exc()
        print("Shutting down.")


def execute(command: str, interface: Interface):
    commands = {
        "save": (save, interface),
        "exit": (exit_game, None),
        "history": (history, interface),
        "next": (next, interface),
        "state": (state, interface),
        "delete": (delete_save, None),
        "transfer": (transfer, interface),
        "secure": (secure, interface),
        "optimal": (optimal, interface),
        "laws": (laws, interface),
        "promote": (promote, interface),
        "recruit": (recruit, interface),
        "fight": (fight, interface)
    }
    commands["help"] = (help, commands.keys())

    answer = command.split(' ')
    answer[0] = fill_command(answer[0], commands.keys())
    if len(answer[0]) == 0:
        print("Invalid command. Enter help for a list of"
              " commands.")
    elif len(answer[0]) > 1:
        strin = ""
        for option in answer[0]:
            strin += option
            strin += " "
        print(strin)
    else:
        answer[0] = answer[0][0]
        if answer[0] in commands:
            commands[answer[0]][0](answer, commands[answer[0]][1])
        else:
            print("Invalid command. Enter help for a list of"
                  " commands.")
