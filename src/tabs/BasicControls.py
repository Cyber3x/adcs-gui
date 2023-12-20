import math

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton


class BasicControls(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        # Create a layout for the raw data tab
        self.layout_main_vertical: QVBoxLayout = QVBoxLayout(self)
        self.layout_main_vertical.addWidget(QLabel("Data Visualization:"))

        self.plot = pg.PlotWidget()
        self.plot.showGrid(True, True)
        self.plot.setLabel('left', 'Angle', 'deg')
        self.plot.setLabel('bottom', 'Time offset', 'ms')
        self.plot.setBackground('transparent')
        self.layout_main_vertical.addWidget(self.plot)

        self.setLayout(self.layout_main_vertical)

        delay_ms = 1
        history_buffer_time_ms = 2000

        self.my_data = np.empty(0)
        self.my_data_max_len = int(history_buffer_time_ms / delay_ms)
        self.plot.setXRange(history_buffer_time_ms, 0)
        self.plot.setYRange(-360, 360)

        self.counter = 0
        self.timer = QTimer()
        self.timer.setInterval(delay_ms)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()

        # ---- INPUT BOXES LAYOUT START ----
        self.layout_main_vertical.addWidget(QLabel("Primitive Control:"))
        self.command_inputs: list[QLineEdit] = []
        self.send_buttons: list[QPushButton] = []

        for i in range(4):
            layout = QHBoxLayout()

            command_input = QLineEdit()
            command_input.setText(str(i + 1))
            self.command_inputs.append(command_input)

            clear_command_button = QPushButton("Clear")
            clear_command_button.clicked.connect(command_input.clear)

            send_button = QPushButton("Send")
            send_button.clicked.connect(self.on_send_button_clicked)
            self.send_buttons.append(send_button)

            layout.addWidget(clear_command_button)
            layout.addWidget(command_input)
            layout.addWidget(send_button)
            self.layout_main_vertical.addLayout(layout)
        # ---- INPUT BOXES LAYOUT END ----

    def on_send_button_clicked(self):
        sender_button = self.sender()
        index = self.send_buttons.index(sender_button)
        line_edit = self.command_inputs[index]
        text = line_edit.text()
        print(f"Sending command: {text}")

    def recurring_timer(self):
        value = math.sin(self.counter) * 360
        self.update_graph(value)
        self.counter += 0.005

    def update_graph(self, value: float):
        if len(self.my_data) >= self.my_data_max_len:
            self.my_data = np.roll(self.my_data, -1)
            self.my_data[-1] = value
        else:
            self.my_data = np.append(self.my_data, value)

        self.plot.clear()
        self.plot.plot(self.my_data, pen=pg.mkPen('r', width=1))

        self.my_data = self.my_data[-self.my_data_max_len:]
