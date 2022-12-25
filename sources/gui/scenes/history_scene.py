from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, cast, overload

from PySide6.QtCore import (QAbstractTableModel, QModelIndex,
                            QPersistentModelIndex, Qt)
from PySide6.QtWidgets import (QComboBox, QGridLayout, QLabel, QMessageBox,
                               QPushButton, QTableView, QHeaderView)

from ...abstract_interface.history import History
from ...auxiliaries.enums import (Class_Name,
                                  Resource)
from ...cli.cli_commands import get_month_string
from ..auxiliaries import crashing_slot
from .abstract_scene import Abstract_Scene

if TYPE_CHECKING:
    from ..command_window import Command_Window


class Data_Type(Enum):
    population = 0  # cla
    resources = 1  # res
    prices = 2  # res
    modifiers = 3  # mod
    population_changes = 4  # cla
    resource_changes = 5  # res
    total_resources = 6  # res
    employment = 7  # cla + gov
    wages = 8  # cla + gov
    happiness = 9  # cla


class Modifiers(Enum):
    starving = 0
    freezing = 1
    promoted_from = 2
    demoted_from = 3
    promoted_to = 4
    demoted_to = 5

    @staticmethod
    def converted_name(value: int) -> str:
        name = Modifiers(value).name.title()
        result = ""
        for character in name:
            if character == '_':
                result += ' '
            else:
                result += character
        return result


def make_raw(string: str) -> str:
    string = string.lower()
    result = ""
    for character in string:
        if character == ' ':
            result += '_'
        else:
            result += character
    return result


class SetDataFailed(Exception):
    """
    Raised when the user tries to view an invalid range of months.
    """


class History_Model(QAbstractTableModel):
    def __init__(
        self, history: History, parent: Scene_History
    ) -> None:
        super().__init__(parent)
        self._parent = parent
        self._data_functions = [
            history.population, history.resources, history.prices,
            history.growth_modifiers, history.population_change,
            history.resources_change, history.total_resources,
            history.employment, history.employment, history.happiness
        ]
        self._data_type: Data_Type | None = None
        self._data: list[dict[str, float]] | \
            list[dict[str, bool]] | None = None
        self._begin_month = 0

    def set_data(self, type: Data_Type, target: str | None = None) -> None:
        self.beginResetModel()
        begin, end = self._parent.get_range()
        data = self._data_functions[type.value]()[begin:end + 1]
        if type in {Data_Type.resources, Data_Type.resource_changes}:
            data = cast(list[dict[str, dict[str, float]]], data)
            if target is None:
                raise TypeError("With this data type target mustn't be None")
            data = [month_data[target] for month_data in data]
        elif type in {Data_Type.employment, Data_Type.wages}:
            data = cast(list[dict[str, tuple[float, float]]], data)
            data = [{
                key: value[type.value - Data_Type.employment.value]
                for key, value
                in month_data.items()
            } for month_data in data]
        elif type == Data_Type.modifiers:
            data = cast(list[dict[str, dict[str, bool]]], data)
            if target is None or target == "government":
                QMessageBox.warning(
                    self._parent, "Warning",
                    "Invalid target for the chosen data"
                )
                raise SetDataFailed
            data = [month_data[target] for month_data in data]
        else:
            data = cast(list[dict[str, float]], data)
        self._data = data
        self._data_type = type
        self._begin_month = begin
        self.endResetModel()

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        if self._data is None:
            return 0

        return len(self._data)

    def columnCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        if self._data is None:
            return 0

        if self._data_type == Data_Type.modifiers:
            return len(Modifiers)
        elif self._data_type in {
            Data_Type.resources, Data_Type.resource_changes,
            Data_Type.prices, Data_Type.total_resources
        }:
            return len(Resource)
        elif self._data_type in {Data_Type.employment, Data_Type.wages}:
            return len(Class_Name) + 1
        else:
            return len(Class_Name)

    @overload
    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int
    ) -> str | None:
        ...

    @overload
    def headerData(
        self, section: int, orientation: Qt.Orientation
    ) -> str:
        ...

    def headerData(
        self, section: int, orientation: Qt.Orientation,
        role: int = Qt.DisplayRole
    ) -> str | None:
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if self._data_type == Data_Type.modifiers:
                    return Modifiers.converted_name(section)
                elif self._data_type in {
                    Data_Type.resources, Data_Type.resource_changes,
                    Data_Type.prices, Data_Type.total_resources
                }:
                    return Resource(section).name.title()
                elif self._data_type in {Data_Type.employment,
                                         Data_Type.wages}:
                    if section == 4:
                        return "Government"
                    else:
                        return Class_Name(section).name.title()
                else:
                    return Class_Name(section).name.title()
            else:
                return get_month_string(self._begin_month + section)

    def data(
        self, index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.DisplayRole
    ) -> Any:
        if self._data is None:
            return ""

        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            column = make_raw(self.headerData(column, Qt.Horizontal))
            return self._data[row][column]


class History_Button(QPushButton):
    def __init__(
        self, text: str, type: Data_Type, target: bool,
        model: History_Model, parent: Scene_History
    ) -> None:
        super().__init__(text, parent)
        self._parent = parent
        self.type = type
        self.target = target
        self.model = model
        self.clicked[None].connect(  # type: ignore
            self.clicked_slot
        )

    @crashing_slot
    def clicked_slot(self) -> None:
        try:
            self._parent.set_govt_available(self.type != Data_Type.modifiers)
            if self.target:
                self.model.set_data(self.type, self._parent.get_target())
            else:
                self.model.set_data(self.type)
            self._parent.last_clicked = self
            self._parent.set_target_enabled(self.target)
        except SetDataFailed:
            pass


class Scene_History(Abstract_Scene):
    def __init__(self, parent: Command_Window) -> None:
        super().__init__(parent)
        self._parent = parent
        self.state = parent.interface.state
        self.main_layout = QGridLayout(self)
        self.last_clicked: History_Button | None = None

        self.top_buttons: list[QPushButton] = []
        right_center: Qt.Alignment = Qt.AlignRight | Qt.AlignVCenter

        labels = [
            "Population", "Resources", "Prices", "Growth modifiers",
            "Population changes", "Resource changes", "Total resources",
            "Employment", "Wages", "Happiness"
        ]
        self.model = History_Model(self._parent.interface.history, self)
        button_font = QPushButton().font()
        button_font.setPointSize(7)
        for i, (type, text) in enumerate(zip(Data_Type, labels)):
            button = History_Button(
                text, type,
                type in {Data_Type.resources, Data_Type.resource_changes,
                         Data_Type.modifiers},
                self.model, self
            )
            button.setFont(button_font)
            self.main_layout.addWidget(button, 0, i)
            self.top_buttons.append(button)

        self.target_label = QLabel("Target class:")
        self.target_label.setAlignment(right_center)
        self.main_layout.addWidget(self.target_label, 1, 0, 1, 2)

        self.target_box = QComboBox()
        self.target_box.addItems([
            "nobles", "artisans", "peasants", "others", "government"
        ])
        self.target_box.setCurrentIndex(0)
        self.target_box.activated[int].connect(  # type: ignore
            self.combo_box_changed
        )
        self.main_layout.addWidget(self.target_box, 1, 2)

        self.range_label = QLabel("Months range:")
        self.range_label.setAlignment(right_center)
        self.main_layout.addWidget(self.range_label, 1, 3, 1, 2)

        self.begin_box = QComboBox()
        self.begin_box.activated[int].connect(  # type: ignore
            self.combo_box_changed
        )
        self.main_layout.addWidget(self.begin_box, 1, 5, 1, 2)

        self.end_box = QComboBox()
        self.end_box.activated[int].connect(  # type: ignore
            self.combo_box_changed
        )
        self.main_layout.addWidget(self.end_box, 1, 7, 1, 2)

        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setMinimumHeight(370)
        self.table_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.main_layout.addWidget(self.table_view, 2, 0, 1, 10)

        self.setLayout(self.main_layout)
        self.update()

    def combo_box_changed(self, new_index: int) -> None:
        if self.last_clicked is not None:
            self.last_clicked.clicked_slot()

    def update(self) -> None:
        old_begin = self.begin_box.currentIndex()
        self.begin_box.clear()
        self.begin_box.addItems([
            get_month_string(i).strip()
            for i in range(self.state.year * 12 + self.state.month.value)
        ])
        if old_begin != -1:
            self.begin_box.setCurrentIndex(old_begin)
        else:
            self.begin_box.setCurrentIndex(0)

        self.end_box.clear()
        self.end_box.addItems([
            get_month_string(i).strip()
            for i in range(self.state.year * 12 + self.state.month.value)
        ])
        self.end_box.setCurrentIndex(
            self.state.year * 12 + self.state.month.value - 1
        )

        if self.last_clicked is not None:
            self.last_clicked.clicked_slot()

    def get_target(self) -> str:
        return self.target_box.currentData(Qt.DisplayRole)

    def get_range(self) -> tuple[int, int]:
        begin = self.begin_box.currentIndex()
        end = self.end_box.currentIndex()
        if end < begin:
            QMessageBox.warning(
                self, "Warning", "This range of months is not valid."
            )
            raise SetDataFailed
        return begin, end

    def set_target_enabled(self, enabled: bool):
        self.target_box.setEnabled(enabled)

    def set_govt_available(self, available: bool):
        if available:
            if self.target_box.count() == 4:
                self.target_box.addItem("government")
        else:
            if self.get_target() == "government":
                self.target_box.setCurrentIndex(0)
            if self.target_box.count() == 5:
                self.target_box.removeItem(4)
