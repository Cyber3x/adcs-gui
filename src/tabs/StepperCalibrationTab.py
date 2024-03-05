import json
import os.path
from json.decoder import JSONDecodeError

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QMessageBox,
                             QLabel, QSlider, QPushButton, QLineEdit, QFileDialog)

from core.communication import send_command
from stores.GlobalStore import State
from utils.utils import create_debounce_timer, action_to_button, custom_JSON_encoder
from validators.DoubleValidator import DoubleValidator

axes = ["X", "Y", "Z"]
stepper_value_slider_scalar = 10
debounce_timer_ms = 300


class StepperCalibrationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.parent = parent

        self.layout_main = QVBoxLayout(self)
        self.layout_main.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_main.setSpacing(10)

        self.layout_main.addLayout(self.create_toolbar())

        self.layout_stepper_controls = QHBoxLayout()

        for axis in axes:
            stepper_controls = _StepperControls(axis_name=axis, parent=self)
            self.layout_stepper_controls.addWidget(stepper_controls)

        self.layout_main.addLayout(self.layout_stepper_controls)

        self.setLayout(self.layout_main)

    def create_toolbar(self):
        toolbar = QHBoxLayout()
        toolbar.setAlignment(Qt.AlignmentFlag.AlignLeft)

        save_stepper_values_action = QAction("Save values")
        save_stepper_values_action.triggered.connect(self.save_stepper_values_file)
        save_stepper_values_action.setShortcut("Ctrl+S")

        open_stepper_values_action = QAction("Open values")
        open_stepper_values_action.triggered.connect(self.open_stepper_values_file)
        open_stepper_values_action.setShortcut("Ctrl+O")

        toolbar.addWidget(action_to_button(open_stepper_values_action))
        toolbar.addWidget(action_to_button(save_stepper_values_action))

        return toolbar

    def save_stepper_values_file(self):
        filters = "JavaScript Object Notation (*.json)"
        filename, selected_filter = QFileDialog.getSaveFileName(
            self,
            caption="Save stepper values",
            directory="stepper_values.json",
            filter=filters,
            initialFilter=filters,
        )

        if not filename:
            return

        with open(filename, "w") as f:
            json.dump(State().stepper_values, f, default=custom_JSON_encoder, indent=4)

    def open_stepper_values_file(self):
        caption = "Open stepper values"  # Empty uses default caption
        inital_dir = ""  # Empty uses current folder
        filters = "JavaScript Object Notation (*.json)"
        initial_filter = "All files (*.*)"

        filename, selected_filter = QFileDialog.getOpenFileName(
            self,
            caption=caption,
            directory=inital_dir,
            filter=filters,
            initialFilter=initial_filter,
        )

        if not filename or not os.path.isfile(filename):
            return

        # TODO: create a loader class so this is moved to there, here it should only be a few lines of code to save and laod data

        with open(filename, "r") as f:
            try:
                data = json.load(f)
            except JSONDecodeError as e:
                print("json error")
                QMessageBox.critical(
                    self,
                    "Invalid JSON",
                    f"The opened file is not a valid JSON file.\n\n"
                    f"{e.msg}",
                    buttons=QMessageBox.StandardButton.Ok,
                    defaultButton=QMessageBox.StandardButton.Ok,
                )
                return

        validation_error = State().stepper_values.update(data)

        if validation_error:
            print("validation error")
            QMessageBox.critical(
                self,
                "Invalid Data Format",
                f"{validation_error.message}\n\n"
                "The format of the JSON file is invalid. Thus, the file cannot be opened.\nYou can try to fix the "
                "file manually or create a new one.",
                buttons=QMessageBox.StandardButton.Ok,
                defaultButton=QMessageBox.StandardButton.Ok,
            )


class _StepperControls(QWidget):
    def __init__(self, axis_name: str, parent=None):
        super().__init__(parent=parent)

        self.axis_name = axis_name
        self.parent = parent

        self.stepper_value = getattr(State().stepper_values, axis_name)

        self.layout_main = QVBoxLayout(self)
        self.layout_main.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_main.setContentsMargins(0, 0, 0, 0)

        # Axis name label
        self.label_axis_name = QLabel(f"{axis_name}")
        font = self.label_axis_name.font()
        font.setPointSize(20)
        self.label_axis_name.setFont(font)
        self.label_axis_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_main.addWidget(self.label_axis_name)

        # Stepper value input
        self.stepper_value_input = QLineEdit()
        self.stepper_value_input.setText(str(self.stepper_value.get()) + "%")
        self.stepper_value_input.returnPressed.connect(
            lambda: self.stepper_value.set(
                float(self.stepper_value_input.text())
            )
        )
        self.stepper_value_input.setValidator(DoubleValidator(0.0, 100.0, 2))
        self.stepper_value.add_callback(lambda x: self.stepper_value_input.setText(str(x) + "%"))
        self.layout_main.addWidget(self.stepper_value_input)

        # Stepper value slider
        self.stepper_value_slider = QSlider(Qt.Orientation.Horizontal)
        self.stepper_value_slider.setMinimum(0)
        self.stepper_value_slider.setMaximum(100 * stepper_value_slider_scalar)
        self.stepper_value_slider.setSingleStep(1)
        self.stepper_value_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.stepper_value_slider.setTickInterval(int(10 * stepper_value_slider_scalar))
        self.stepper_value_slider.valueChanged.connect(self.handle_stepper_value_slider_value_changed)
        self.stepper_value.add_callback(
            lambda value: self.stepper_value_slider.setValue(
                int(value * stepper_value_slider_scalar)
            )
        )
        self.layout_main.addWidget(self.stepper_value_slider)

        # --- LAYOUT STEPPER CONTROL SLIDER START ---
        self.layout_stepper_fine_controls = QHBoxLayout()

        self.decrease_stepper_value_0_01 = QPushButton("-0.01")
        self.decrease_stepper_value_0_1 = QPushButton("-0.1")
        self.decrease_stepper_value_1 = QPushButton("-1")

        self.increase_stepper_value_1 = QPushButton("+1")
        self.increase_stepper_value_0_1 = QPushButton("+0.1")
        self.increase_stepper_value_0_01 = QPushButton("+0.01")

        self.layout_stepper_fine_controls.addWidget(self.decrease_stepper_value_0_01)
        self.layout_stepper_fine_controls.addWidget(self.decrease_stepper_value_0_1)
        self.layout_stepper_fine_controls.addWidget(self.decrease_stepper_value_1)
        self.layout_stepper_fine_controls.addWidget(self.increase_stepper_value_1)
        self.layout_stepper_fine_controls.addWidget(self.increase_stepper_value_0_1)
        self.layout_stepper_fine_controls.addWidget(self.increase_stepper_value_0_01)

        self.decrease_stepper_value_0_01.clicked.connect(lambda: self.handle_stepper_value_decrease(0.01))
        self.decrease_stepper_value_0_1.clicked.connect(lambda: self.handle_stepper_value_decrease(0.1))
        self.decrease_stepper_value_1.clicked.connect(lambda: self.handle_stepper_value_decrease(1))
        self.increase_stepper_value_1.clicked.connect(lambda: self.handle_stepper_value_increase(1))
        self.increase_stepper_value_0_1.clicked.connect(lambda: self.handle_stepper_value_increase(0.1))
        self.increase_stepper_value_0_01.clicked.connect(lambda: self.handle_stepper_value_increase(0.01))

        self.layout_main.addLayout(self.layout_stepper_fine_controls)
        # --- LAYOUT STEPPER CONTROL SLIDER END --

        # center button
        self.center_command_button = QPushButton("Center")
        self.center_command_button.clicked.connect(
            lambda: self.stepper_value.set(50)
        )
        self.layout_main.addWidget(self.center_command_button)

        self.setLayout(self.layout_main)

        # Debounce timer for buttons, so that the stepper doesn't get spammed with commands
        # the timer will be reset if another button is pressed before the timer runs out
        self.debounce_timer = create_debounce_timer(debounce_timer_ms, self.send_stepper_value)

    def send_stepper_value(self):
        send_command(f"stepper {axes.index(self.axis_name)} move {self.stepper_value.get()}")

    def handle_stepper_value_slider_value_changed(self, value):
        self.stepper_value.set(value / stepper_value_slider_scalar)
        self.debounce_timer.start()

    def handle_stepper_value_decrease(self, value):
        new_value = max(0, self.stepper_value.get() - value)
        new_value = round(new_value, 2)
        self.stepper_value.set(new_value)

        self.debounce_timer.start()

    def handle_stepper_value_increase(self, value):
        new_value = min(100, self.stepper_value.get() + value)
        new_value = round(new_value, 2)
        self.stepper_value.set(new_value)

        self.debounce_timer.start()
