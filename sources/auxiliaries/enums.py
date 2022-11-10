from enum import Enum, auto


class Month(Enum):
    January = 0
    February = 1
    March = 2
    April = 3
    May = 4
    June = 5
    July = 6
    August = 7
    September = 8
    October = 9
    November = 10
    December = 11


class Class_Name(Enum):
    nobles = 0
    artisans = 1
    peasants = 2
    others = 3


class Resource(Enum):
    food = auto()
    wood = auto()
    stone = auto()
    iron = auto()
    tools = auto()
    land = auto()


class Soldier(Enum):
    knights = auto()
    footmen = auto()


CLASS_NAME_STR = [class_name.name for class_name in Class_Name]
RESOURCE_STR = [resource.name for resource in Resource]
SOLDIER_STR = [soldier.name for soldier in Soldier]
