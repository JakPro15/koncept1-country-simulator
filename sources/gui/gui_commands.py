import sys
from PySide6.QtWidgets import (
    QDialog, QMessageBox
)

from sources.gui.number_select_dialog import Number_Select_Dialog
from ..state.state_data import (
    EveryoneDeadError,
    RebellionError
)
from .transfer_dialog import Transfer_Dialog
from ..cli.cli_commands import ShutDownCommand
from .save_dialog import Save_Dialog
from .auxiliaries import crashing_slot
from .execute_dialog import Execute_Dialog
from ..auxiliaries.constants import CLASS_NAME_TO_INDEX, INBUILT_RESOURCES
from math import floor


class GUI_Commands(QDialog):
    @crashing_slot
    def execute_command(self):
        real_stdout = sys.stdout
        real_stdin = sys.stdin
        try:
            dialog = Execute_Dialog(self)
            dialog.exec()
        finally:
            sys.stdout = real_stdout
            sys.stdin = real_stdin

    @crashing_slot
    def next_month(self):
        try:
            self.interface.next_month()
        except EveryoneDeadError as e:
            QMessageBox.information(self, "Game Over", "GAME OVER\n"
                                    "There is not a living person left in your"
                                    " country.")
            raise ShutDownCommand from e
        except RebellionError as e:
            QMessageBox.information(self, "Game Over", "GAME OVER\n"
                                    f"{str(e).title()} have rebelled.")
            raise ShutDownCommand from e
        self.update()

    @crashing_slot
    def save_game(self):
        save_dialog = Save_Dialog(False, self)
        save_dialog.exec()

    @crashing_slot
    def delete_save(self):
        save_dialog = Save_Dialog(True, self)
        save_dialog.exec()

    @crashing_slot
    def transfer(self, class_name: str):
        transfer_dialog = Transfer_Dialog(class_name, self)
        transfer_dialog.exec()

    @crashing_slot
    def promote(self, class_name: str):
        lower_class = self.interface.state.classes[
            CLASS_NAME_TO_INDEX[class_name]].lower_class

        cost = (INBUILT_RESOURCES[class_name] -
                INBUILT_RESOURCES[lower_class.class_name])
        res_maxes = self.interface.state.government.real_resources / cost
        res_max = floor(min(res_maxes.values()))

        if res_max <= 0:
            QMessageBox.warning(self, "Warning", "The government does not have"
                                " enough resources for this operation")
        elif floor(lower_class.population) <= 0:
            QMessageBox.warning(self, "Warning", "The class to promote from is"
                                " empty")
        else:
            promote_dialog = Number_Select_Dialog(
                0, min(floor(lower_class.population), res_max), "Promote",
                f"How many {lower_class.class_name} do you want to"
                f" promote to {class_name}?"
            )
            number = promote_dialog.exec()

            self.interface.force_promotion(class_name, number)
            self.update()
