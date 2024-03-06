from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit

from modules.AxisControls import AxisControls
from stores.GlobalStore import State, IMU_Data_Dict, axes, PIDParametersData
from utils.utils import action_to_button


class AngularVelocityControlTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.state = State()

        self.axis_controls: dict[str, AxisControls] = {}

        self.layout_main_vertical: QVBoxLayout = QVBoxLayout(self)
        self.layout_main_vertical.setSpacing(10)

        self.layout_data_display: QHBoxLayout = QHBoxLayout()
        self.layout_main_vertical.addLayout(self.layout_data_display)

        self.layout_axis_controls: QHBoxLayout = QHBoxLayout()

        for axis in axes:
            axis_controller = AxisControls(axis_name=axis, parent=self)
            self.axis_controls[axis] = axis_controller
            self.layout_axis_controls.addWidget(axis_controller)

        self.layout_main_vertical.addLayout(self.layout_axis_controls)

        self.layout_main_vertical.addWidget(_PIDParameterInput(
            self, self.state.dc_motor_values.angular_velocity_control["tuning_paramiters"]
        ))

        self.setLayout(self.layout_main_vertical)
        self.state.IMU_angle_data.add_callback(self.update_graphs)

    def update_graphs(self, IMU_angle_data: IMU_Data_Dict):
        for axis in axes:
            self.axis_controls[axis].update_graph(IMU_angle_data[axis])


class _PIDParameterInput(QWidget):
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
        print(self.PIDData)

    def load_PID_values_file(self):
        print("Loading PID values")
