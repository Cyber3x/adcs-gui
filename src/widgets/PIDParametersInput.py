from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit

from stores.GlobalStore import PIDParametersData
from utils.saving_and_loading import save_json_data, load_json_data
from utils.utils import action_to_button, int_or_float_to_str
from validators import DoubleValidator
from validators.schemas import PID_values_schema


class PIDParametersInput(QWidget):
    def __init__(self, parent, PIDData: PIDParametersData):
        super().__init__()
        self.parent = parent
        self.PIDData = PIDData

        self.layout_main = QHBoxLayout(self)
        self.layout_main.setContentsMargins(0, 0, 0, 0)

        self.layout_kp = QHBoxLayout()
        self.layout_ki = QHBoxLayout()
        self.layout_kd = QHBoxLayout()

        self.kp_input = QLineEdit()
        self.ki_input = QLineEdit()
        self.kd_input = QLineEdit()

        # Add validators to the input fields
        self.kp_input.setValidator(DoubleValidator(0, 100))
        self.ki_input.setValidator(DoubleValidator(0, 100))
        self.kd_input.setValidator(DoubleValidator(0, 100))

        # Update the PID values when the input fields change
        self.kp_input.textChanged.connect(lambda x: PIDData.P.set(float(x or 0)))
        self.ki_input.textChanged.connect(lambda x: PIDData.I.set(float(x or 0)))
        self.kd_input.textChanged.connect(lambda x: PIDData.D.set(float(x or 0)))

        # When editing is finished, set the input fields to the current PID values
        # This prevents the users from leaving the field empty
        self.kp_input.editingFinished.connect(lambda: self.kp_input.setText(int_or_float_to_str(PIDData.P.get())))
        self.ki_input.editingFinished.connect(lambda: self.ki_input.setText(int_or_float_to_str(PIDData.I.get())))
        self.kd_input.editingFinished.connect(lambda: self.kd_input.setText(int_or_float_to_str(PIDData.D.get())))

        # Update the input fields when the values change
        self.PIDData.P.add_callback(lambda x: self.kp_input.setText(int_or_float_to_str(x)))
        self.PIDData.I.add_callback(lambda x: self.ki_input.setText(int_or_float_to_str(x)))
        self.PIDData.D.add_callback(lambda x: self.kd_input.setText(int_or_float_to_str(x)))

        self.layout_kp.addWidget(QLabel("Kp:"))
        self.layout_kp.addWidget(self.kp_input)

        self.layout_ki.addWidget(QLabel("Ki:"))
        self.layout_ki.addWidget(self.ki_input)

        self.layout_kd.addWidget(QLabel("Kd:"))
        self.layout_kd.addWidget(self.kd_input)

        save_PID_values_action = QAction("Save values")
        save_PID_values_action.triggered.connect(self.save_PID_values_file)
        save_PID_values_action.setShortcut("Ctrl+S")

        load_PID_values_action = QAction("Open values")
        load_PID_values_action.triggered.connect(self.load_PID_values_file)
        load_PID_values_action.setShortcut("Ctrl+O")

        self.layout_main.addWidget(action_to_button(save_PID_values_action))
        self.layout_main.addWidget(action_to_button(load_PID_values_action))
        self.layout_main.addLayout(self.layout_kp)
        self.layout_main.addLayout(self.layout_ki)
        self.layout_main.addLayout(self.layout_kd)

        # Set the input fields to the initial values
        self.kp_input.setText(int_or_float_to_str(PIDData.P.get()))
        self.ki_input.setText(int_or_float_to_str(PIDData.I.get()))
        self.kd_input.setText(int_or_float_to_str(PIDData.D.get()))

        self.setLayout(self.layout_main)

    def save_PID_values_file(self):
        save_json_data(self.PIDData, "Save PID values", "PID_values_angular_velocity.json")

    def load_PID_values_file(self):
        loaded_data = load_json_data(PID_values_schema, "Load PID values")
        self.PIDData.update(loaded_data)
