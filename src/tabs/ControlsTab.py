import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from modules.AxisControls import AxisControls
from stores.GlobalStore import State

axes = ["X", "Y", "Z"]


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

        for axis in axes:
            axis_controller = AxisControls(axis_name=axis, parent=self)
            self.axis_controls[axis] = axis_controller
            self.layout_axis_controls.addWidget(axis_controller)

        self.layout_main_vertical.addLayout(self.layout_axis_controls)

        self.setLayout(self.layout_main_vertical)

    def update_graphs(self):
        for axis in axes:
            self.axis_controls[axis].update_graph()
