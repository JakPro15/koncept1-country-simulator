from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (QCheckBox, QGridLayout, QLabel, QLineEdit,
                               QPushButton)

from ...auxiliaries.enums import Class_Name, Resource
from ...state.state_data import InvalidCommandError
from .abstract_scene import Abstract_Scene

if TYPE_CHECKING:
    from ..command_window import Command_Window


class Scene_Laws(Abstract_Scene):
    def __init__(self, parent: Command_Window) -> None:
        super().__init__(parent)
        self._parent = parent
        self.state = parent.interface.state
        self.main_layout = QGridLayout(self)

        self.left_labels: list[QLabel] = []
        self.specific_labels: list[QLabel] = []
        self.law_line_edits: list[QLineEdit] = []
        row = 0
        right_bottom: Qt.Alignment = Qt.AlignRight | Qt.AlignBottom
        right_center: Qt.Alignment = Qt.AlignRight | Qt.AlignCenter

        for law in ["tax_personal", "tax_property", "tax_income"]:
            label = self.get_label_widget(law, right_bottom)
            self.left_labels.append(label)
            self.main_layout.addWidget(label, row, 0, 1, 2)

            for class_name in Class_Name:
                class_label = QLabel(f"{class_name.name.title()}:")
                class_label.setAlignment(right_center)
                self.specific_labels.append(class_label)
                self.main_layout.addWidget(class_label, row, 2)

                line_edit = QLineEdit("")
                if law == "tax_personal":
                    line_edit.setValidator(QRegularExpressionValidator(
                        r"^\d+\.\d*$"
                    ))
                    line_edit.setToolTip("Value must be nonnegative.")
                else:
                    line_edit.setValidator(QRegularExpressionValidator(
                        r"^((1\.0*)|(0\.\d*))$"
                    ))
                    line_edit.setToolTip(
                        "Value must be between 0 and 1 (including endpoints)."
                    )
                self.law_line_edits.append(line_edit)
                self.main_layout.addWidget(line_edit, row, 3)

                row += 1

        self.main_layout.setColumnMinimumWidth(4, 50)
        for row, law in enumerate(["wage_minimum", "wage_government"]):
            label = self.get_label_widget(law, right_center)
            self.left_labels.append(label)
            self.main_layout.addWidget(label, row, 5, 1, 3)

            line_edit = QLineEdit("")
            line_edit.setValidator(QRegularExpressionValidator(
                r"^((1\.0*)|(0\.\d*))$"
            ))
            line_edit.setToolTip(
                "Value must be between 0 and 1 (including endpoints)."
            )
            self.law_line_edits.append(line_edit)
            self.main_layout.addWidget(line_edit, row, 8)

        label = self.get_label_widget("wage_autoregulation", right_center)
        self.left_labels.append(label)
        self.main_layout.addWidget(label, 2, 5, 1, 3)

        self.autoregulation_checkbox = QCheckBox()
        self.main_layout.addWidget(self.autoregulation_checkbox, 2, 8)

        label = self.get_label_widget("max_prices", right_bottom)
        self.left_labels.append(label)
        self.main_layout.addWidget(label, 3, 5, 1, 2)

        row = 3
        for resource in Resource:
            class_label = QLabel(f"{resource.name.title()}:")
            class_label.setAlignment(right_center)
            self.specific_labels.append(class_label)
            self.main_layout.addWidget(class_label, row, 7)

            line_edit = QLineEdit("")
            line_edit.setValidator(QRegularExpressionValidator(
                r"^(\d+\.\d*|inf)$"
            ))
            line_edit.setToolTip("Value must be nonnegative.")
            self.law_line_edits.append(line_edit)
            self.main_layout.addWidget(line_edit, row, 8)

            row += 1

        self.confirm_button = QPushButton("Save changes")
        self.main_layout.addWidget(self.confirm_button, 100, 0, 1, 9)
        self.confirm_button.clicked[None].connect(  # type: ignore
            self.set_laws)

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

    @staticmethod
    def get_label_widget(law: str, alignment: Qt.Alignment) -> QLabel:
        """
        Returns a label widget for the given law.
        """
        label, tooltip = Scene_Laws.get_label_and_tooltip(law)
        label_widget = QLabel(label)
        label_widget.setToolTip(tooltip)
        label_widget.setAlignment(alignment)
        return label_widget

    def update(self) -> None:
        i = 0
        for law in ["tax_personal", "tax_property", "tax_income"]:
            taxes = self.state.sm.tax_rates[
                law.split('_')[1]
            ]
            for class_name in Class_Name:
                self.law_line_edits[i].setText(str(taxes[class_name]))
                i += 1

        min_wage = self.state.sm.others_minimum_wage
        self.law_line_edits[i].setText(str(min_wage))
        i += 1

        govt_wage = max(self.state.government.wage,
                        self.state.sm.others_minimum_wage)
        self.law_line_edits[i].setText(str(govt_wage))
        self.law_line_edits[i].setEnabled(
            not self.state.government.wage_autoregulation
        )
        i += 1
        self.autoregulation_checkbox.setChecked(
            self.state.government.wage_autoregulation
        )

        max_prices = self.state.sm.max_prices
        for resource in Resource:
            self.law_line_edits[i].setText(str(max_prices[resource]))
            i += 1

    def set_laws(self) -> None:
        i = 0
        for law in ["tax_personal", "tax_property", "tax_income"]:
            for class_name in Class_Name:
                self.state.sm.tax_rates[law.split('_')[1]][class_name] = \
                    float(self.law_line_edits[i].text())
                i += 1

        self.state.sm.others_minimum_wage = \
            float(self.law_line_edits[i].text())
        i += 1

        self.state.government.wage = max(float(self.law_line_edits[i].text()),
                                         self.state.sm.others_minimum_wage)
        i += 1
        self.state.government.wage_autoregulation = \
            self.autoregulation_checkbox.isChecked()

        self.state.sm.max_prices
        for resource in Resource:
            self.state.sm.max_prices[resource] = \
                float(self.law_line_edits[i].text())
            i += 1

        self.update()
