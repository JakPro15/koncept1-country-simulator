from .interface import Interface
from .constants import MONTHS
import os.path


class Command_Line_Interface:
    def __init__(self):
        print("Do you want to start a new game, or continue a previous one?")
        print("0 - new game")
        print("1 - load a save file")
        answer = input("Your choice: ").strip()
        while answer not in {'0', '1'}:
            print("Invalid choice")
            answer = input("Your choice: ").strip()

        if answer == '0':
            filename = "saves/starting.json"
        else:
            filename = "saves/" + input("Enter a filename: ").strip()
            while not os.path.isfile(filename):
                print("Invalid filename")
                filename = "saves/" + input("Enter a filename: ").strip()
        print("Loading " + filename)
        interface = Interface()
        interface.load_data(filename)

        while True:
            print("Choose an action")
            print("0 - exit")
            print("1 - proceed to next month")
            print("2 - view history")
            answer = input("Your choice: ").strip()
            while answer not in {'0', '1', '2'}:
                print("Invalid choice")
                answer = input("Your choice: ").strip()

            if answer == '0':
                break
            elif answer == '1':
                interface.next_month()
            elif answer == '2':
                if len(interface.history) == 0:
                    print("History is currently empty.")
                    continue
                print("What data do you want to see?")
                print("0 - population")
                print("1 - resources")
                answer2 = input("Your choice: ").strip()
                while answer2 not in {'0', '1'}:
                    print("Invalid choice")
                    answer2 = input("Your choice: ").strip()
                if answer2 == '0':
                    data = interface.history.population_stats()
                elif answer2 == '1':
                    data = interface.history.resources_stats()

                print("See history from one or multiple months?")
                print("0 - last month")
                print("1 - 1 year back")
                print("2 - 5 years back")
                print("3 - entire history")
                answer2 = input("Your choice: ").strip()
                while answer2 not in [str(number) for number in range(4)]:
                    print("Invalid choice")
                    answer2 = input("Your choice: ").strip()

                current_month = MONTHS.index(interface.state.month) + \
                    12 * interface.state.year
                if answer2 == '0':
                    print(data[-1])
                else:
                    if answer2 == '1':
                        begin_month = max(0, current_month - 12)
                        data = data[begin_month:]
                    elif answer2 == '2':
                        begin_month = max(0, current_month - 60)
                        data = data[begin_month:]
                    elif answer2 == '3':
                        data = data[0:]
                    for index, month_data in enumerate(data):
                        year = index // 12
                        month = index % 12
                        print(f"{MONTHS[month]: >9} {year}: {month_data}")
