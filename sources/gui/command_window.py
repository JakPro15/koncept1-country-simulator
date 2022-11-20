from __future__ import annotations

from math import floor
from typing import cast

from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QMessageBox,
                               QPushButton, QVBoxLayout, QWidget)

from ..abstract_interface.interface import (Interface, MalformedSaveError,
                                            NoSoldiersError, SaveAccessError)
from ..auxiliaries import globals
from ..auxiliaries.constants import (CLASS_TO_SOLDIER, INBUILT_RESOURCES,
                                     RECRUITABLE_PART, RECRUITMENT_COST)
from ..auxiliaries.enums import Class_Name
from ..cli.cli_commands import ShutDownCommand
from ..gui.number_select_dialog import (Number_Select_Dialog,
                                        NumberSelectRejected)
from ..gui.resources_display import Resources_Display
from ..state.state_data_base_and_do_month import (EveryoneDeadError,
                                                  RebellionError)
from .auxiliaries import crashing_slot
from .execute_dialog import Execute_Dialog
from .optimal_dialog import Optimal_Dialog
from .recruit_dialog import RecruitDialog
from .save_dialog import Save_Dialog
from .scenes.abstract_scene import Abstract_Scene
from .scenes.classes_scene import Scene_Classes
from .scenes.govt_scene import Scene_Govt
from .scenes.military_scene import Scene_Military
from .secure_dialog import Secure_Dialog
from .scenes.laws_scene import Scene_Laws
from .transfer_dialog import Transfer_Dialog


class Command_Window(QDialog):
    def __init__(self, dirname: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        if globals.debug:
            self.setWindowTitle("Koncept 1 - debug mode")
        else:
            self.setWindowTitle("Koncept 1")

        # Load the game
        self.interface = Interface()
        try:
            self.interface.load_data(dirname)
        except SaveAccessError:
            QMessageBox.critical(self, "Critical Error", "Failed to open the"
                                 " save file. Shutting down.")
            raise
        except MalformedSaveError:
            QMessageBox.critical(self, "Critical Error", "The program"
                                 " encountered an error while loading the save"
                                 " file. Probably the file format is invalid."
                                 " Shutting down.")
            raise

        # 0th layer - header label and some command buttons
        self.l0_layout = QHBoxLayout()

        self.l0_header = QLabel()
        self.l0_layout.addWidget(self.l0_header)

        self.l0_layout.addStretch()

        self.l0_exec_button = QPushButton("Execute command")
        self.l0_exec_button.clicked[None].connect(  # type: ignore
            self.execute_command)
        self.l0_layout.addWidget(self.l0_exec_button)

        self.l0_next_button = QPushButton("End month")
        self.l0_next_button.clicked[None].connect(  # type: ignore
            self.next_month)
        self.l0_layout.addWidget(self.l0_next_button)

        self.l0_save_button = QPushButton("Save game")
        self.l0_save_button.clicked[None].connect(  # type: ignore
            self.save_game)
        self.l0_layout.addWidget(self.l0_save_button)

        self.l0_del_button = QPushButton("Delete save")
        self.l0_del_button.clicked[None].connect(  # type: ignore
            self.delete_save)
        self.l0_layout.addWidget(self.l0_del_button)

        self.l0_layout.addSpacing(10)

        # 1st layer: General state information
        self.l1_header = QLabel("Current prices:")
        self.l1_prices = Resources_Display()

        self.l1_layout = QHBoxLayout()
        self.l1_layout.addSpacing(10)
        self.l1_layout.addWidget(self.l1_header)
        self.l1_prices.add_to_layout(self.l1_layout)

        # 2nd layer: General state information
        self.l2_header = QLabel("Government resources:")
        self.l2_resources = Resources_Display()
        self.l2_population = QLabel("Population:", self)

        self.l2_layout = QHBoxLayout()
        self.l2_layout.addSpacing(10)
        self.l2_layout.addWidget(self.l2_header)
        self.l2_resources.add_to_layout(self.l2_layout)
        self.l2_layout.addWidget(self.l2_population)

        # 3rd layer: Various menus buttons
        self.l3_menus_buttons = [
            QPushButton("Classes", self),
            QPushButton("Government", self),
            QPushButton("Military", self),
            QPushButton("Laws", self),
            QPushButton("History", self)
        ]
        self.l3_menus_buttons[0].clicked[None].connect(  # type: ignore
            crashing_slot(lambda: self.set_scene(Scene_Classes(self)))
        )
        self.l3_menus_buttons[1].clicked[None].connect(  # type: ignore
            crashing_slot(lambda: self.set_scene(Scene_Govt(self)))
        )
        self.l3_menus_buttons[2].clicked[None].connect(  # type: ignore
            crashing_slot(lambda: self.set_scene(Scene_Military(self)))
        )
        self.l3_menus_buttons[3].clicked[None].connect(  # type: ignore
            crashing_slot(lambda: self.set_scene(Scene_Laws(self)))
        )

        self.l3_layout = QHBoxLayout()
        for button in self.l3_menus_buttons:
            self.l3_layout.addWidget(button)

        self.layout_ = QVBoxLayout()
        self.layout_.addLayout(self.l0_layout)
        self.layout_.addLayout(self.l1_layout)
        self.layout_.addLayout(self.l2_layout)
        self.layout_.addLayout(self.l3_layout)
        self.layout_.addSpacing(15)
        self.layout_.addStretch()
        self.setLayout(self.layout_)

        self.scene_set: Abstract_Scene | None = None
        self.update()

        self.setMinimumSize(900, 600)

    def set_scene(self, new_scene: Abstract_Scene) -> None:
        if self.scene_set:
            self.layout_.removeWidget(self.scene_set)
            self.scene_set.deleteLater()
        self.scene_set = new_scene
        self.layout_.insertWidget(4, new_scene)

    def update(self) -> None:
        # Main menu
        save_string = self.interface.save_name
        month = f"{self.interface.state.month.name}" \
                f" {self.interface.state.year}"
        if save_string is None:
            save_string = f"New game: {month}"
        else:
            save_string = f'Loaded game "{save_string}": {month}'
        self.l0_header.setText(save_string)

        prices = round(self.interface.state.prices, 4)
        self.l1_prices.set_resources(prices)

        ress = round(self.interface.state.government.resources, 2)
        self.l2_resources.set_resources(ress)
        self.l2_population.setText(
            f"Population: {round(self.interface.state.total_population)}"
        )
        # Scene
        if self.scene_set:
            self.scene_set.update()

    @crashing_slot
    def execute_command(self) -> None:
        dialog = Execute_Dialog(self)
        dialog.exec()
        self.update()

    @crashing_slot
    def next_month(self) -> None:
        try:
            self.interface.next_month()
        except EveryoneDeadError as e:
            QMessageBox.information(self, "Game Over", "GAME OVER\n"
                                    "There is not a living person left in your"
                                    " country.")
            raise ShutDownCommand from e
        except RebellionError as e:
            QMessageBox.information(self, "Game Over", "GAME OVER\n"
                                    f"{e.class_name.title()} have rebelled.")
            raise ShutDownCommand from e
        self.update()

    @crashing_slot
    def save_game(self) -> None:
        save_dialog = Save_Dialog(self, False)
        save_dialog.exec()

    @crashing_slot
    def delete_save(self) -> None:
        save_dialog = Save_Dialog(self, True)
        save_dialog.exec()

    @crashing_slot
    def transfer(self, class_name: Class_Name) -> None:
        transfer_dialog = Transfer_Dialog(class_name, self)
        transfer_dialog.exec()

    @crashing_slot
    def promote(self, class_name: Class_Name) -> None:
        lower_class = self.interface.state.classes[class_name].lower_class

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
                f"How many {lower_class.class_name.name} do you want to"
                f" promote to {class_name.name}?"
            )
            try:
                number = promote_dialog.exec()
                self.interface.force_promotion(class_name, number)
                self.update()
            except NumberSelectRejected:
                pass

    @crashing_slot
    def secure(self) -> None:
        secure_dialog = Secure_Dialog(self)
        secure_dialog.exec()

    @crashing_slot
    def optimal(self) -> None:
        optimal_dialog = Optimal_Dialog(self)
        optimal_dialog.exec()

    @crashing_slot
    def recruit(self, class_name: Class_Name) -> None:
        social_class = self.interface.state.classes[class_name]
        soldier_type = CLASS_TO_SOLDIER[class_name]
        cost = RECRUITMENT_COST[soldier_type]
        res_maxes = self.interface.state.government.real_resources / cost
        res_max = floor(min(res_maxes.values()))

        if res_max <= 0:
            QMessageBox.warning(self, "Warning", "The government does not have"
                                " enough resources for this operation")
        elif floor(social_class.population) <= 0:
            QMessageBox.warning(self, "Warning", "The class to recruit from is"
                                " empty")
        else:
            recruit_dialog = RecruitDialog(
                0, min(floor(social_class.population * RECRUITABLE_PART),
                       res_max), social_class
            )
            try:
                number = recruit_dialog.exec()
                self.interface.recruit(class_name, number)
                self.update()
            except NumberSelectRejected:
                pass

    @crashing_slot
    def fight(self, target: str) -> None:
        target_message: str = ""
        if target == "crime":
            target_message = "brigands"
        elif target == "plunder":
            target_message = "neighbours for loot"
        elif target == "land":
            target_message = "neighbours for land"

        reply = cast(QMessageBox.StandardButton, QMessageBox.question(
            self, "Confirm", f"Do you really want to attack {target_message}"
            " with all your soldiers?", QMessageBox.Yes, QMessageBox.No
        ))
        if reply == QMessageBox.Yes:
            try:
                results = self.interface.fight(target)

                dead_soldiers = \
                    results[1] if globals.debug else round(results[1], 0)
                reply_message = "The battle has been" + \
                    (" won.\n" if results[0] else " lost.\n")
                reply_message += f"{dead_soldiers.knights} knight" + \
                    f"{'s' if dead_soldiers.knights != 1 else ''} and "\
                    f"{dead_soldiers.footmen} " + \
                    f"footm{'e' if dead_soldiers.footmen != 1 else 'a'}n" + \
                    " died.\n"
                if target == "crime":
                    dead_brigands = \
                        results[2] if globals.debug else round(results[2])
                    reply_message += f"{dead_brigands} brigand" + \
                        f"{'s' if dead_brigands != 1 else ''} died."
                elif target == "conquest":
                    reply_message += f"Conquered {round(results[2], 2)} land."
                elif target == "plunder":
                    reply_message += f"Plundered {round(results[2], 2)}" + \
                        " food, wood, stone, iron and tools."
                QMessageBox.information(self, "Fight results", reply_message)
            except NoSoldiersError:
                QMessageBox.warning(
                    self, "Warning", "You don't have enough soldiers to"
                    " attack."
                )
            self.update()
