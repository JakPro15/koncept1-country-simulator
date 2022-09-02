import traceback

from ..abstract_interface.interface import (Interface, MalformedSaveError,
                                            SaveAccessError)
from .cli_commands import COMMANDS, ShutDownCommand, fill_command


def command_line_interface(dirname_to_load: str) -> None:
    try:
        print("Loading saves/" + dirname_to_load)
        interface = Interface()
        try:
            interface.load_data(dirname_to_load)
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
    answer = command.split(' ')
    given_cmd_options = fill_command(answer[0], COMMANDS.keys())
    if len(given_cmd_options) == 0:
        print("Invalid command. Enter help for a list of"
              " commands.")
    elif len(given_cmd_options) > 1:
        strin = ""
        for option in given_cmd_options:
            strin += option
            strin += " "
        print(strin)
    else:
        command = given_cmd_options[0]
        if command in COMMANDS:
            COMMANDS[command](answer, interface)
        else:
            print("Invalid command. Enter help for a list of"
                  " commands.")
