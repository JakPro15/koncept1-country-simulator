from .number_select_dialog import Number_Select_Dialog
from PySide6.QtWidgets import QWidget
from ..state.social_classes.class_file import Class
from ..auxiliaries.constants import CLASS_TO_SOLDIER
from .auxiliaries import ValueLabel, crashing_slot


class RecruitDialog(Number_Select_Dialog):
    def __init__(self, min: int, max: int, social_class: Class,
                 parent: QWidget | None = None) -> None:
        self.social_class = social_class
        header: str = f"How many {social_class.class_name.name} do you want" \
            f" to recruit as {CLASS_TO_SOLDIER[social_class.class_name].name}?"
        super().__init__(min, max, "Recruit", header, parent)

        self.happiness_label = ValueLabel(
            "Estimated happiness", social_class.happiness, rounding=2
        )
        self.main_layout.addWidget(self.happiness_label)

    @crashing_slot
    def slider_changed(self, slider_value: int) -> None:
        super().slider_changed(slider_value)
        self.update_happiness_label(slider_value)

    @crashing_slot
    def edit_changed(self, text: str) -> None:
        super().edit_changed(text)
        self.update_happiness_label(self.slider.value())

    def update_happiness_label(self, recruited: int) -> None:
        self.happiness_label.value = self.social_class.happiness + \
            self.social_class.recruitment_happiness(recruited)
