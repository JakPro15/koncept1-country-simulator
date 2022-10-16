import traceback

from ..abstract_interface.interface import (AlreadyFoughtError,
                                            EmptyClassError, Interface,
                                            InvalidArgumentError,
                                            MalformedSaveError,
                                            NoSoldiersError,
                                            NotEnoughClassPopulation,
                                            NotEnoughClassResources,
                                            NotEnoughGovtResources,
                                            SaveAccessError)
from ..state.state_data_base_and_do_month import (EveryoneDeadError,
                                                  RebellionError)
from .cli_commands import COMMANDS, ShutDownCommand, fill_command
from ..auxiliaries import globals


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
    except (KeyboardInterrupt, EOFError):
        print("Shutting down.")
    except BaseException as e:
        print(f"An unexpected exception of type {e.__class__.__name__} has"
              " occurred and the program will be terminated.")
        if globals.debug:
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
        command = given_cmd_options.pop()
        if command in COMMANDS:
            try:
                COMMANDS[command](answer, interface)
            except NotEnoughGovtResources:
                print("The government does not have enough resources for this"
                      " operation.")
            except NotEnoughClassPopulation:
                print("The chosen class does not have enough population.")
            except NotEnoughClassResources:
                print("The chosen class does not have enough resources for"
                      " this operation.")
            except EmptyClassError:
                print("The chosen class is empty.")
            except NoSoldiersError:
                print("The government does not have enough soldiers for this"
                      " operation.")
            except AlreadyFoughtError:
                print("The government cannot conduct attacks more than once a"
                      " month.")
            except InvalidArgumentError as e:
                print(f"Invalid syntax: {e}. See help for proper usage of"
                      f" {command} command")
            except EveryoneDeadError:
                print("GAME OVER")
                print("There is not a living person left in your country.")
                raise ShutDownCommand
            except RebellionError as e:
                print("GAME OVER")
                print(f"{str(e).title()} have rebelled.")
                raise ShutDownCommand
        else:
            print("Invalid command. Enter help for a list of"
                  " commands.")
