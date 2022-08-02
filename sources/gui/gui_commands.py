from PySide6.QtWidgets import (
    QDialog, QMessageBox
)
from ..state.state_data import (
    EveryoneDeadError,
    RebellionError
)
from .transfer_dialog import Transfer_Dialog
from ..cli.cli_commands import ShutDownCommand
from .save_dialog import Save_Dialog
from .auxiliaries import crashing_slot


class GUI_Commands(QDialog):
    @crashing_slot
    def next_month(self):
        try:
            self.interface.next_month()
        except EveryoneDeadError:
            QMessageBox.information(self, "Game Over", "GAME OVER\n"
                                    "There is not a living person left in your"
                                    " country.")
            raise ShutDownCommand
        except RebellionError as e:
            QMessageBox.information(self, "Game Over", "GAME OVER\n"
                                    f"{str(e).title()} have rebelled.")
            raise ShutDownCommand
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
