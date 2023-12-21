import math

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QSlider,
                             QLineEdit)

from core.ObservableValue import create_observable_value
from validators.DoubleValidator import DoubleValidator
from validators.IntValidator import IntValidator
from widgets.SeparatorLine import SeparatorLine

MAX_NUM_OF_DATAPOINTS = 200


class AxisState:
    def __init__(self):
        self.angle = create_observable_value(0)  # rad
        self.angular_velocity = create_observable_value(0.0)  # rad/
        self.angular_velocity_datapoints_real = np.zeros(200)
        # self.angular_velocity_datapoints_target = np.zeros(MAX_NUM_OF_DATAPOINTS)


class AxisControls(QWidget):
    def __init__(self, state: AxisState, axis_name: str, parent=None):
        super().__init__(parent)
        self.axis_name = axis_name
        self.state = state
        self.parent = parent

        layout_main_vertical = QVBoxLayout()
        layout_main_vertical.setContentsMargins(10, 0, 10, 0)
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
        layout_main_vertical.addWidget(stop_flywheel_button)

        set_rotation_rate_label = QLabel("Set rotation rate [rad/s]")
        set_rotation_rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_main_vertical.addWidget(set_rotation_rate_label)

        # ---- FLYWHEEL CONTROLS LAYOUT START ----
        layout_flywheel_controls = QHBoxLayout()

        self.flywheel_set_rotation_rate_input = QLineEdit()
        self.flywheel_set_rotation_rate_input.setValidator(
            DoubleValidator(min_value=-math.pi * 2, max_value=math.pi * 2)
        )
        layout_flywheel_controls.addWidget(self.flywheel_set_rotation_rate_input)
        self.state.angular_velocity.add_callback(lambda x: self.flywheel_set_rotation_rate_input.setText(str(x)))

        flywheel_set_rotation_rate_set_button = QPushButton("Set")
        flywheel_set_rotation_rate_set_button.clicked.connect(self.handle_set_rotation_rate_button_clicked)
        layout_flywheel_controls.addWidget(flywheel_set_rotation_rate_set_button)

        layout_main_vertical.addLayout(layout_flywheel_controls)
        # ---- FLYWHEEL CONTROLS LAYOUT END ----

        self.rotation_rate_slider = QSlider()
        #  FIXME: when the input is set to 3 aka 300 whats more than the slider max it get's set to
        #   the max of 200 when the slider is again set to 300 it gets set and isn't reset
        self.state.angular_velocity.add_callback(self.callback_angular_velocity_changed)
        self.rotation_rate_slider.setOrientation(Qt.Orientation.Horizontal)
        self.rotation_rate_slider.setRange(-200, 200)
        self.rotation_rate_slider.setSingleStep(1)
        self.rotation_rate_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.rotation_rate_slider.valueChanged.connect(self.handle_rotation_rate_slider_change)
        layout_main_vertical.addWidget(self.rotation_rate_slider)

        rotate_fixed_angle_label = QLabel("Rotate fixed angle [deg]")
        rotate_fixed_angle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_main_vertical.addWidget(rotate_fixed_angle_label)

        # ---- FLYWHEEL ROTATE FIXED ANGLE CONTROLS LAYOUT START ----
        layout_h = QHBoxLayout()

        self.angle_input = QLineEdit()
        self.angle_input.setValidator(IntValidator())
        self.angle_input.textChanged.connect(self.handle_angle_input_change)
        self.state.angle.add_callback(lambda x: self.angle_input.setText(str(x)))
        layout_h.addWidget(self.angle_input)

        rotate_button = QPushButton("Rotate")
        layout_h.addWidget(rotate_button)

        layout_main_vertical.addLayout(layout_h)
        # ---- FLYWHEEL ROTATE FIXED ANGLE CONTROLS LAYOUT END ----

        self.rotation_angle_slider = QSlider()
        self.rotation_angle_slider.setOrientation(Qt.Orientation.Horizontal)
        self.rotation_angle_slider.setRange(-360, 360)
        self.rotation_angle_slider.setSingleStep(1)
        self.rotation_angle_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.rotation_angle_slider.valueChanged.connect(lambda x: self.state.angle.set(x))
        self.state.angle.add_callback(lambda x: self.rotation_angle_slider.setValue(int(x)))
        layout_main_vertical.addWidget(self.rotation_angle_slider)

        # AXIS ANGLE PLOT
        self.angular_velocity_plot = pg.PlotWidget()
        self.angular_velocity_plot.showGrid(True, True)
        self.angular_velocity_plot.setLabel('left', 'Angular velocity', 'rad/s')
        self.angular_velocity_plot.setBackground('transparent')
        self.angular_velocity_plot.setYRange(-2, 2)

        layout_main_vertical.addWidget(self.angular_velocity_plot)

        self.setLayout(layout_main_vertical)

    def update_graph_data(self, new_value):
        # if len(self.state.angular_velocity_datapoints_real) < MAX_NUM_OF_DATAPOINTS:
        #     self.state.angular_velocity_datapoints_real = np.append(self.state.angular_velocity_datapoints_real,
        #                                                             new_value)
        # else:
        self.state.angular_velocity_datapoints_real = np.roll(self.state.angular_velocity_datapoints_real, -1)
        self.state.angular_velocity_datapoints_real[-1] = new_value

        self.update_graph()

    def update_graph(self):
        self.angular_velocity_plot.clear()

        pen_color_real_data = ["r", "g", "b"][["X", "Y", "Z"].index(self.axis_name)]
        # pen_color_target_data = [(255, 100, 100), (100, 255, 100), (100, 100, 255)][
        #     ["X", "Y", "Z"].index(self.axis_name)]

        datapoints = [self.state.angular_velocity_datapoints_real]
        colors = [pen_color_real_data]

        for i in range(len(datapoints)):
            pen = pg.mkPen(color=colors[i])
            self.angular_velocity_plot.plot(datapoints[i], pen=pen)

    def callback_angular_velocity_changed(self, value):
        self.rotation_rate_slider.setValue(int(value * 100))

    def handle_angle_input_change(self):
        text = self.angle_input.text()
        if text and text != '-':
            degs = int(text)
            self.state.angle.set(degs)

    def handle_rotation_rate_slider_change(self):
        rads = self.rotation_rate_slider.value() / 100
        self.state.angular_velocity.set(rads)

    def handle_set_rotation_rate_button_clicked(self):
        rads = float(self.flywheel_set_rotation_rate_input.text())
        self.current_ang_velocity = rads
        self.state.angular_velocity.set(rads)

    def handle_send_move_command_button_clicked(self):
        if not self.stepper_move_steps_input.text():
            return

        steps = int(self.stepper_move_steps_input.text())
        self.parent.parent.serial_communication_tab.write_data(
            f'stepper {["X", "Y", "Z"].index(self.axis_name)} {steps}')
