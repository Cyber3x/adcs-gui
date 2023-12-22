import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from stores.GlobalStore import State, IMU_Data_Dict, axes


def create_plot_widget() -> pg.PlotWidget:
    plot = pg.PlotWidget()
    plot.showGrid(True, True)
    plot.setBackground('transparent')
    plot.enableAutoRange('y', True)
    return plot


class RawDataGraphs(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.state = State()

        self.layout_main = QVBoxLayout(self)

        self.angle_plot = create_plot_widget()
        self.angle_plot.setLabel('left', 'Angle', 'deg')
        self.angle_plot.getPlotItem().addLegend()

        self.acceleration_plot = create_plot_widget()
        self.acceleration_plot.setLabel('left', 'Acceleration', 'm/s^2')

        self.gyroscope_plot = create_plot_widget()
        self.gyroscope_plot.setLabel('left', 'Angular velocity', 'deg/s')

        self.temperature_plot = create_plot_widget()
        self.temperature_plot.setLabel('left', 'Temperature', '°C')

        self.layout_main.addWidget(self.angle_plot)
        self.layout_main.addWidget(self.gyroscope_plot)
        self.layout_main.addWidget(self.acceleration_plot)
        self.layout_main.addWidget(self.temperature_plot)

        # create a plot lines for temperature
        pen = pg.mkPen(color='cyan')
        self.temperature_plot_line = self.temperature_plot.plot(self.state.IMU_temperature_data.data, pen=pen)

        self.axis_plots = {
            self.angle_plot: self.state.IMU_angle_data.data,
            self.acceleration_plot: self.state.IMU_acceleration_data.data,
            self.gyroscope_plot: self.state.IMU_gyroscope_data.data,
        }

        self.axis_plot_lines: Dict[pg.PlotWidget, Dict[Axis, pg.PlotItem]] = {}

        for plot, data in self.axis_plots.items():
            self.axis_plot_lines[plot] = {}
            for axis, axis_data in data.items():
                pen_color = ['r', 'g', 'b'][axes.index(axis)]
                pen = pg.mkPen(color=pen_color)
                self.axis_plot_lines[plot][axis] = plot.plot(axis_data, pen=pen)

        self.state.IMU_angle_data.add_callback(self.update_angle_plot)
        self.state.IMU_acceleration_data.add_callback(self.update_acceleration_plot)
        self.state.IMU_gyroscope_data.add_callback(self.update_gyroscope_plot)
        self.state.IMU_temperature_data.add_callback(self.update_temperature_plot)

        self.setLayout(self.layout_main)

    def _update_plot_lines(self, plot: pg.PlotWidget, IMU_data_dict: IMU_Data_Dict):
        for axis, data in IMU_data_dict.items():
            self.axis_plot_lines[plot][axis].setData(data)

    def update_angle_plot(self, IMU_angle_data: IMU_Data_Dict):
        self._update_plot_lines(self.angle_plot, IMU_angle_data)

    def update_acceleration_plot(self, IMU_acceleration_data: IMU_Data_Dict):
        self._update_plot_lines(self.acceleration_plot, IMU_acceleration_data)

    def update_gyroscope_plot(self, IMU_gyroscope_data: IMU_Data_Dict):
        self._update_plot_lines(self.gyroscope_plot, IMU_gyroscope_data)

    def update_temperature_plot(self, IMU_temperature_data: np.ndarray):
        self.temperature_plot_line.setData(IMU_temperature_data)
