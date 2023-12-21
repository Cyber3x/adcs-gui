from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                             QPushButton, QPlainTextEdit, QLineEdit,
                             QHBoxLayout)


class ClickablePlainTextEdit(QPlainTextEdit):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class RawDataTab(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        # Create a layout for the raw data tab
        self.raw_data_layout = QVBoxLayout(self)

        # Create and add widgets to the layout
        self.text_area = ClickablePlainTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setMaximumBlockCount(50)
        self.raw_data_layout.addWidget(QLabel("Raw Data:"))
        self.raw_data_layout.addWidget(self.text_area)

        # ------ COMMAND INPUT LAYOUT START ------
        self.command_input_layout = QHBoxLayout()

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command here...")
        self.command_input_layout.addWidget(self.command_input)
        self.command_input.returnPressed.connect(self.on_send_button_clicked)
        self.text_area.clicked.connect(self.command_input.setFocus)

        self.send_command_button = QPushButton("Send")
        self.command_input_layout.addWidget(self.send_command_button)
        self.send_command_button.clicked.connect(self.on_send_button_clicked)

        self.raw_data_layout.addLayout(self.command_input_layout)
        # ------ COMMAND INPUT LAYOUT END ------

        # Clear button
        self.clear_button = QPushButton("Clear")
        self.raw_data_layout.addWidget(self.clear_button)
        self.clear_button.clicked.connect(self.text_area.clear)

        # Set up the layout for the raw data tab
        self.setLayout(self.raw_data_layout)

    def on_send_button_clicked(self):
        command = self.command_input.text()
        if not command:
            return

        self.command_input.clear()
        # self.text_area.appendPlainText(command)
        self.parent.serial_communication_tab.write_data(command)
