import math

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QSlider,
                             QLineEdit)

from validators.DoubleValidator import DoubleValidator
from validators.IntValidator import IntValidator


class AxisControls(QWidget):
    def __init__(self, axis_name: str, parent=None):
        super().__init__(parent)
        self.axis_name = axis_name
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

        flywheel_set_rotation_rate_set_button = QPushButton("Set")
        flywheel_set_rotation_rate_set_button.clicked.connect(self.handle_set_rotation_rate_button_clicked)
        layout_flywheel_controls.addWidget(flywheel_set_rotation_rate_set_button)

        layout_main_vertical.addLayout(layout_flywheel_controls)
        # ---- FLYWHEEL CONTROLS LAYOUT END ----

        self.rotation_rate_slider = QSlider()
        #  FIXME: when the input is set to 3 aka 300 whats more than the slider max it get's set to
        #   the max of 200 when the slider is again set to 300 it gets set and isn't reset
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
        layout_main_vertical.addWidget(self.rotation_angle_slider)

        # AXIS ANGLE PLOT
        self.angular_velocity_plot = pg.PlotWidget()
        self.angular_velocity_plot.showGrid(True, True)
        self.angular_velocity_plot.setLabel('left', 'Angular velocity', 'rad/s')
        self.angular_velocity_plot.setBackground('transparent')
        self.angular_velocity_plot.setYRange(-2, 2)
        self.angular_velocity_plot.enableAutoRange()

        layout_main_vertical.addWidget(self.angular_velocity_plot)

        self.setLayout(layout_main_vertical)

    def update_graph(self, angle_datapoints: np.ndarray):
        self.angular_velocity_plot.clear()

        pen_color_real_data = ["r", "g", "b"][["X", "Y", "Z"].index(self.axis_name)]

        pen = pg.mkPen(color=pen_color_real_data)
        self.angular_velocity_plot.plot(angle_datapoints, pen=pen)

    def callback_angular_velocity_changed(self, value):
        self.rotation_rate_slider.setValue(int(value * 100))

    def handle_angle_input_change(self):
        text = self.angle_input.text()
        if text and text != '-':
            degs = int(text)

    def handle_rotation_rate_slider_change(self):
        rads = self.rotation_rate_slider.value() / 100

    def handle_set_rotation_rate_button_clicked(self):
        rads = float(self.flywheel_set_rotation_rate_input.text())
        self.current_ang_velocity = rads

    def handle_send_move_command_button_clicked(self):
        if not self.stepper_move_steps_input.text():
            return

        steps = int(self.stepper_move_steps_input.text())
        self.parent.parent.serial_communication_tab.write_data(
            f'stepper {["X", "Y", "Z"].index(self.axis_name)} {steps}')
