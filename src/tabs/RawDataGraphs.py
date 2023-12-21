import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from stores.GlobalStore import State, IMU_Data_Dict, axes


class RawDataGraphs(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.state = State()

        self.layout_main = QVBoxLayout(self)

        self.angle_plot = pg.PlotWidget()
        self.angle_plot.showGrid(True, True)
        self.angle_plot.setLabel('left', 'Angle', 'deg')
        self.angle_plot.setBackground('transparent')
        self.angle_plot.enableAutoRange('y', True)
        self.layout_main.addWidget(self.angle_plot)

        self.acceleration_plot = pg.PlotWidget()
        self.acceleration_plot.showGrid(True, True)
        self.acceleration_plot.setLabel('left', 'Acceleration', 'm/s^2')
        self.acceleration_plot.setBackground('transparent')
        self.acceleration_plot.enableAutoRange('y', True)
        self.layout_main.addWidget(self.acceleration_plot)

        self.gyroscope_plot = pg.PlotWidget()
        self.gyroscope_plot.showGrid(True, True)
        self.gyroscope_plot.setLabel('left', 'Angular velocity', 'deg/s')
        self.gyroscope_plot.setBackground('transparent')
        self.gyroscope_plot.enableAutoRange('y', True)
        self.layout_main.addWidget(self.gyroscope_plot)

        self.temperature_plot = pg.PlotWidget()
        self.temperature_plot.showGrid(True, True)
        self.temperature_plot.setLabel('left', 'Temperature', '°C')
        self.temperature_plot.setBackground('transparent')
        self.temperature_plot.enableAutoRange('y', True)
        self.layout_main.addWidget(self.temperature_plot)

        self.state.IMU_angle_data.add_callback(self.update_angle_plot)
        self.state.IMU_acceleration_data.add_callback(self.update_acceleration_plot)
        self.state.IMU_gyroscope_data.add_callback(self.update_gyroscope_plot)
        self.state.IMU_temperature_data.add_callback(self.update_temperature_plot)

    def update_angle_plot(self, IMU_angle_data: IMU_Data_Dict):
        self.angle_plot.clear()

        for axis in axes:
            pen_color = ['r', 'g', 'b'][axes.index(axis)]
            pen = pg.mkPen(color=pen_color)
            self.angle_plot.plot(IMU_angle_data[axis], pen=pen)

    def update_acceleration_plot(self, IMU_acceleration_data: IMU_Data_Dict):
        self.acceleration_plot.clear()

        for axis in axes:
            pen_color = ['r', 'g', 'b'][axes.index(axis)]
            pen = pg.mkPen(color=pen_color)
            self.acceleration_plot.plot(IMU_acceleration_data[axis], pen=pen)

    def update_gyroscope_plot(self, IMU_gyroscope_data: IMU_Data_Dict):
        self.gyroscope_plot.clear()

        for axis in axes:
            pen_color = ['r', 'g', 'b'][axes.index(axis)]
            pen = pg.mkPen(color=pen_color)
            self.gyroscope_plot.plot(IMU_gyroscope_data[axis], pen=pen)

    def update_temperature_plot(self, IMU_temperature_data: np.ndarray):
        self.temperature_plot.clear()

        pen_color = 'cyan'
        pen = pg.mkPen(color=pen_color)
        self.temperature_plot.plot(IMU_temperature_data, pen=pen)
