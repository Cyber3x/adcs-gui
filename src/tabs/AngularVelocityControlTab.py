from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from modules.AxisControls import AxisControls
from stores.GlobalStore import State, IMU_Data_Dict, axes


class AngularVelocityControlTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.state = State()

        self.axis_controls: dict[str, AxisControls] = {}

        self.layout_main_vertical: QVBoxLayout = QVBoxLayout(self)

        self.layout_data_display: QHBoxLayout = QHBoxLayout()

        self.layout_main_vertical.addLayout(self.layout_data_display)

        self.layout_axis_controls: QHBoxLayout = QHBoxLayout()

        for axis in axes:
            axis_controller = AxisControls(axis_name=axis, parent=self)
            self.axis_controls[axis] = axis_controller
            self.layout_axis_controls.addWidget(axis_controller)

        self.layout_main_vertical.addLayout(self.layout_axis_controls)

        self.setLayout(self.layout_main_vertical)
        self.state.IMU_angle_data.add_callback(self.update_graphs)

    def update_graphs(self, IMU_angle_data: IMU_Data_Dict):
        for axis in axes:
            self.axis_controls[axis].update_graph(IMU_angle_data[axis])
