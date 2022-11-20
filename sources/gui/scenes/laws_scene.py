from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGridLayout, QLabel, QLineEdit, QPushButton

from .abstract_scene import Abstract_Scene
from ...state.state_data import InvalidCommandError
from ...auxiliaries.enums import Class_Name
from PySide6.QtCore import Qt
from PySide6.QtGui import QRegularExpressionValidator

if TYPE_CHECKING:
    from ..command_window import Command_Window


class Scene_Laws(Abstract_Scene):
    def __init__(self, parent: Command_Window) -> None:
        super().__init__(parent)
        self._parent = parent
        self.main_layout = QGridLayout(self)

        self.left_labels: list[QLabel] = []
        self.specific_labels: list[QLabel] = []
        self.law_line_edits: list[QLineEdit] = []
        self.law_buttons: list[QPushButton] = []
        row = 0
        right_bottom_align: Qt.Alignment = Qt.AlignRight | Qt.AlignBottom

        for law in ["tax_personal", "tax_property", "tax_income"]:
            label, tooltip = self.get_label_and_tooltip(law)
            label_widget = QLabel(label)
            label_widget.setToolTip(tooltip)
            label_widget.setAlignment(right_bottom_align)
            self.left_labels.append(label_widget)
            self.main_layout.addWidget(label_widget, row, 0, 1, 2)

            for class_name in Class_Name:
                class_label = QLabel(f"{class_name.name.title()}:")
                self.specific_labels.append(class_label)
                self.main_layout.addWidget(class_label, row, 2)

                class_edit = QLineEdit("")
                if law == "tax_personal":
                    class_edit.setValidator(QRegularExpressionValidator(
                        r"^\d+\.\d*$"
                    ))
                    class_edit.setToolTip("Value must be nonnegative.")
                else:
                    class_edit.setValidator(QRegularExpressionValidator(
                        r"^((1\.0*)|(0\.\d*))$"
                    ))
                    class_edit.setToolTip(
                        "Value must be between 0 and 1 (including endpoints)."
                    )
                self.law_line_edits.append(class_edit)
                self.main_layout.addWidget(class_edit, row, 3)

                class_button = QPushButton("Confirm change")
                self.law_buttons.append(class_button)
                self.main_layout.addWidget(class_button, row, 4)

                row += 1

        for law in ["wage_minimum", "wage_government", "wage_autoregulation",
                    "max_prices"]:
            ...

        self.setLayout(self.main_layout)
        self.update()

    @staticmethod
    def get_label_and_tooltip(law: str) -> tuple[str, str]:
        """
        Returns the label and tooltip for the given law, for Laws_Scene's
        widgets.
        """
        if law == "tax_personal":
            return "Taxes per person", "The amount of money taken from the" \
                " class per person in the class"
        elif law == "tax_property":
            return "Property taxes", "What part of a class' resources is" \
                " taken each month as taxes"
        elif law == "tax_income":
            return "Income taxes", "What part of a class' profits from last" \
                " month is taken as taxes"
        elif law == "wage_minimum":
            return "Minimum wage", "Wage is the part of the resources" \
                " produced by employees that is given to the employees"
        elif law == "wage_government":
            return "Government employee wage", "Wage is the part of" \
                " the resources produced by employees that is given to the" \
                " employees"
        elif law == "wage_autoregulation":
            return "Government wage autoregulation", "Toggle whether the" \
                " government employee wage should be regulated automatically"
        elif law == "max_prices":
            return "Maximum prices", "Prices of a resource cannot rise above" \
                " this value"
        else:
            raise InvalidCommandError

    def update(self) -> None:
        row = 0
        for law in ["tax_personal", "tax_property", "tax_income"]:
            taxes = self._parent.interface.state.sm.tax_rates[
                law.split('_')[1]
            ]
            for class_name in Class_Name:
                self.law_line_edits[row].setText(str(taxes[class_name]))
                row += 1
