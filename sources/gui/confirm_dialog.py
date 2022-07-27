from PySide6.QtWidgets import (
    QDialog, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
)


class Confirm_Dialog(QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.label = QLabel(text)
        self.bool_result = False
        self.yes_button = QPushButton("Yes")
        self.yes_button.clicked.connect(self.accept)
        self.no_button = QPushButton("No")
        self.no_button.clicked.connect(self.reject)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.yes_button)
        self.buttons_layout.addWidget(self.no_button)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.label)
        self.main_layout.addLayout(self.buttons_layout)

        self.setLayout(self.main_layout)

    # def accepted(self):
    #     self.bool_result = True
    #     self.reject()

    def exec(self):
        super().exec()
        return self.result() == QDialog.Accepted
