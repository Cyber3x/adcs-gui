from dataclasses import dataclass

import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from modules.AxisControls import AxisState, AxisControls

@dataclass
class State:
    axis_data = {
        "X": AxisState(),
        "Y": AxisState(),
        "Z": AxisState(),
    }


class ControlsTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.state = State()

        self.axis_controls: dict[str, AxisControls] = {}

        self.layout_main_vertical: QVBoxLayout = QVBoxLayout(self)

        self.layout_data_display: QHBoxLayout = QHBoxLayout()

        main_plot = pg.PlotWidget()
        main_plot.showGrid(True, True)
        main_plot.setLabel('left', 'Angle', 'deg')
        main_plot.setBackground('transparent')
        main_plot.setYRange(0, 90)
        self.layout_data_display.addWidget(main_plot)

        self.layout_main_vertical.addLayout(self.layout_data_display)

        self.layout_axis_controls: QHBoxLayout = QHBoxLayout()

        axes = ["X", "Y", "Z"]

        for axis in axes:
            axis_controller = AxisControls(axis_name=axis, state=self.state.axis_data[axis], parent=self)
            self.axis_controls[axis] = axis_controller
            self.layout_axis_controls.addWidget(axis_controller)

        self.layout_main_vertical.addLayout(self.layout_axis_controls)

        self.setLayout(self.layout_main_vertical)
