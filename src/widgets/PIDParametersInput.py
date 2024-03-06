from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit

from stores.GlobalStore import PIDParametersData
from utils.saving_and_loading import save_json_data
from utils.utils import action_to_button


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

        # TODO: add validators
        self.kp_input.textChanged.connect(lambda x: PIDData.P.set(x))
        self.ki_input.textChanged.connect(lambda x: PIDData.I.set(x))
        self.kd_input.textChanged.connect(lambda x: PIDData.D.set(x))

        self.PIDData.P.add_callback(lambda x: self.kp_input.setText(str(x)))
        self.PIDData.I.add_callback(lambda x: self.ki_input.setText(str(x)))
        self.PIDData.D.add_callback(lambda x: self.kd_input.setText(str(x)))

        self.layout_kp.addWidget(QLabel("Kp:"))
        self.layout_kp.addWidget(self.kp_input)

        self.layout_ki.addWidget(QLabel("Ki:"))
        self.layout_ki.addWidget(self.ki_input)

        self.layout_kd.addWidget(QLabel("Kd:"))
        self.layout_kd.addWidget(self.kd_input)

        save_PID_values_action = QAction("Save values")
        save_PID_values_action.triggered.connect(self.save_PID_values_file)
        save_PID_values_action.setShortcut("Ctrl+S")

        load_PID_values_action = QAction("Load values")
        load_PID_values_action.triggered.connect(self.load_PID_values_file)
        load_PID_values_action.setShortcut("Ctrl+O")

        self.layout_main.addWidget(action_to_button(save_PID_values_action))
        self.layout_main.addWidget(action_to_button(load_PID_values_action))
        self.layout_main.addLayout(self.layout_kp)
        self.layout_main.addLayout(self.layout_ki)
        self.layout_main.addLayout(self.layout_kd)

        self.setLayout(self.layout_main)

    def save_PID_values_file(self):
        save_json_data(self.PIDData, "Save PID values", "PID_values_angular_velocity.json")

    def load_PID_values_file(self):
        print("Loading PID values")
