from PySide6.QtWidgets import (
    QApplication, QDialog, QMessageBox
)
from ..state.state_data import (
    EveryoneDeadError,
    RebellionError
)
from ..cli.cli_commands import ShutDownCommand
from .save_dialog import Save_Dialog
import traceback


def crashing_slot(inner):
    def crashing_inner(*args, **kwargs):
        try:
            inner(*args, **kwargs)
        except BaseException:
            if __debug__:
                traceback.print_exc()
            QApplication.exit()
    return crashing_inner


class GUI_Commands(QDialog):
    def update_labels(self):
        resources = round(
            self.interface.state.get_state_data("resources", True), 2
        )
        for label, res in zip(self.top_labels,
                              resources["government"].values()):
            label.setText(
                f"{label.text().split(' ')[0]} {res}"
            )
        self.top_labels[6].setText(
            f"{self.top_labels[6].text().split(' ')[0]} "
            f"{round(self.interface.state.total_population)}"
        )

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
        self.update_labels()

    @crashing_slot
    def save_game(self):
        save_dialog = Save_Dialog(self)
        save_dialog.exec()
