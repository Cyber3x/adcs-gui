import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QSlider,
                             QLineEdit)

from stores.GlobalStore import State, MIN_ANGULAR_VELOCITY, MAX_ANGULAR_VELOCITY
from utils.utils import clamp

# FIXME: This is a temporary solution to the slider not being able to handle floats
# the slider displays the value multiplied by this value but when reading it's divided by this value
SLIDER_SCALAR_VALUE = 100


class AxisAngularVelocityControl(QWidget):
    def __init__(self, axis_name: str, parent=None):
        super().__init__(parent)
        self.axis_name = axis_name
        self.parent = parent
        self.state = State()

        layout_main_vertical = QVBoxLayout()
        layout_main_vertical.setContentsMargins(0, 0, 0, 0)
        layout_main_vertical.setAlignment(Qt.AlignmentFlag.AlignTop)

        axis_name_label = QLabel(f"{axis_name}")
        font = axis_name_label.font()
        font.setPointSize(20)
        axis_name_label.setFont(font)
        axis_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_main_vertical.addWidget(axis_name_label)

        flywheel_label = QLabel("Flywheel control")
        flywheel_label.setContentsMargins(0, 20, 0, 10)
        flywheel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_main_vertical.addWidget(flywheel_label)

        stop_flywheel_button = QPushButton("Stop")
        stop_flywheel_button.clicked.connect(self.handle_stop_button_clicked)
        layout_main_vertical.addWidget(stop_flywheel_button)

        set_rotation_rate_label = QLabel("Set rotation rate [rad/s]")
        set_rotation_rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_main_vertical.addWidget(set_rotation_rate_label)

        # ---- FLYWHEEL CONTROLS LAYOUT START ----
        layout_dc_motor_control = QHBoxLayout()

        self.dc_motor_velocity_input = QLineEdit()
        getattr(self.state.dc_motor_values.angular_velocity_control["values"], axis_name).add_callback(
            lambda x: self.dc_motor_velocity_input.setText(str(x))
        )

        # TODO: Set proper validator
        # self.dc_motor_velocity_input.setValidator()
        layout_dc_motor_control.addWidget(self.dc_motor_velocity_input)

        dc_motor_velocity_set_button = QPushButton("Set")
        dc_motor_velocity_set_button.clicked.connect(self.handle_set_rotation_rate_button_clicked)
        layout_dc_motor_control.addWidget(dc_motor_velocity_set_button)

        layout_main_vertical.addLayout(layout_dc_motor_control)
        # ---- FLYWHEEL CONTROLS LAYOUT END ----

        self.angular_velocity_slider = QSlider()
        self.angular_velocity_slider.setOrientation(Qt.Orientation.Horizontal)
        self.angular_velocity_slider.setRange(MIN_ANGULAR_VELOCITY * SLIDER_SCALAR_VALUE,
                                              MAX_ANGULAR_VELOCITY * SLIDER_SCALAR_VALUE)
        self.angular_velocity_slider.setSingleStep(1)
        self.angular_velocity_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.angular_velocity_slider.valueChanged.connect(self.handle_rotation_rate_slider_change)
        getattr(self.state.dc_motor_values.angular_velocity_control["values"], axis_name).add_callback(
            lambda x: self.angular_velocity_slider.setValue(int(x * SLIDER_SCALAR_VALUE))
        )
        layout_main_vertical.addWidget(self.angular_velocity_slider)

        rotate_fixed_angle_label = QLabel("Rotate fixed angle [deg]")
        rotate_fixed_angle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_main_vertical.addWidget(rotate_fixed_angle_label)

        # AXIS ANGLE PLOT
        self.angular_velocity_plot = pg.PlotWidget()
        self.angular_velocity_plot.showGrid(True, True)
        self.angular_velocity_plot.setLabel('left', 'Angular velocity', 'deg/s')
        self.angular_velocity_plot.setBackground('transparent')
        self.angular_velocity_plot.setYRange(MIN_ANGULAR_VELOCITY, MAX_ANGULAR_VELOCITY)
        self.angular_velocity_plot.enableAutoRange()

        layout_main_vertical.addWidget(self.angular_velocity_plot)

        self.setLayout(layout_main_vertical)

        self.set_intital_values()

    def update_graph(self, angle_datapoints: np.ndarray):
        self.angular_velocity_plot.clear()

        pen_color_real_data = ["r", "g", "b"][["X", "Y", "Z"].index(self.axis_name)]

        pen = pg.mkPen(color=pen_color_real_data)
        self.angular_velocity_plot.plot(angle_datapoints, pen=pen)

    def handle_rotation_rate_slider_change(self):
        getattr(self.state.dc_motor_values.angular_velocity_control["values"], self.axis_name).set(
            self.angular_velocity_slider.value() / SLIDER_SCALAR_VALUE
        )

    def handle_set_rotation_rate_button_clicked(self):
        new_angular_velocity = clamp(
            float(self.dc_motor_velocity_input.text()),
            MIN_ANGULAR_VELOCITY,
            MAX_ANGULAR_VELOCITY
        )

        self.dc_motor_velocity_input.setText(str(new_angular_velocity))

        print(f"set dc motor of axis {self.axis_name} to {new_angular_velocity} rad/s")
        getattr(self.state.dc_motor_values.angular_velocity_control["values"], self.axis_name).set(
            new_angular_velocity
        )

    def handle_stop_button_clicked(self):
        getattr(self.state.dc_motor_values.angular_velocity_control["values"], self.axis_name).set(0)
        self.handle_set_rotation_rate_button_clicked()

    def set_intital_values(self):
        self.dc_motor_velocity_input.setText(
            str(getattr(self.state.dc_motor_values.angular_velocity_control["values"], self.axis_name).get())
        )
        self.angular_velocity_slider.setValue(
            int(
                getattr(self.state.dc_motor_values.angular_velocity_control["values"], self.axis_name)
                .get() * SLIDER_SCALAR_VALUE
            )
        )
