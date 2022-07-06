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
    delete_save
)
from .cli_game_commands import (
    transfer,
    secure,
    optimal,
    laws
)


def command_line_interface(debug, dirname):
    print("Loading saves/" + dirname)
    interface = Interface(debug=debug)
    try:
        interface.load_data(dirname)
    except SaveAccessError:
        print("Failed to open the save file. Shutting down.")
        return
    except MalformedSaveError:
        print("The save file format is invalid, or the program encountered an "
              "error while loading the save file. Shutting down.")
        return

    commands = {
        "help", "save", "exit", "history", "next", "state", "delete",
        "transfer", "secure", "optimal", "laws"
    }

    while True:
        try:
            print("Enter a command. Enter help for a list of commands.")
            answer = input().strip().split(' ')
            answer[0] = fill_command(answer[0], commands)
            if len(answer[0]) == 0:
                print("Invalid command. Enter help for a list of commands.")
            elif len(answer[0]) > 1:
                strin = ""
                for command in answer[0]:
                    strin += command
                    strin += " "
                print(strin)
            else:
                answer[0] = answer[0][0]
                if answer[0] == "help":
                    help(answer, commands)
                elif answer[0] == "save":
                    save(answer, interface)
                elif answer[0] == "exit":
                    raise ShutDownCommand
                elif answer[0] == "history":
                    history(answer, interface)
                elif answer[0] == "next":
                    next(answer, interface)
                elif answer[0] == "state":
                    state(answer, interface)
                elif answer[0] == "delete":
                    delete_save(answer)
                elif answer[0] == "transfer":
                    transfer(answer, interface)
                elif answer[0] == "secure":
                    secure(answer, interface)
                elif answer[0] == "optimal":
                    optimal(answer, interface)
                elif answer[0] == "laws":
                    laws(answer, interface)
                else:
                    print(
                        "Invalid command. Enter help for a list of commands."
                    )
        except ShutDownCommand:
            print("Shutting down.")
            return
