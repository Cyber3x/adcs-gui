import sys

import PyQt6.QtGui as QtGui
from PyQt6.QtWidgets import (QMainWindow, QApplication, QTabWidget)

from tabs.AngularVelocityControlTab import AngularVelocityControlTab
from tabs.RawDataGraphsTab import RawDataGraphsTab
from tabs.RawDataTab import RawDataTab
from tabs.SerialCommunicationTab import SerialCommunicationTab
from tabs.StepperCalibrationTab import StepperCalibrationTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.data = ''

        # create tabs for the main window
        self.tabs = QTabWidget(self)

        self.serial_communication_tab = SerialCommunicationTab(self)
        self.tabs.addTab(self.serial_communication_tab, "Serial Communication Settings")

        self.raw_data_tab = RawDataTab(self)
        self.tabs.addTab(self.raw_data_tab, "Raw Data")

        self.raw_data_graphs = RawDataGraphsTab(self)
        self.tabs.addTab(self.raw_data_graphs, "Raw Data Graphs")

        self.stepper_calibration_tab = StepperCalibrationTab(self)
        self.tabs.addTab(self.stepper_calibration_tab, "Stepper Calibration")

        self.angular_speed_control_tab = AngularVelocityControlTab(self)
        self.tabs.addTab(self.angular_speed_control_tab, "Angular Speed Control")

        self.tabs.setCurrentIndex(4)
        self.setCentralWidget(self.tabs)

        self.serial_communication_tab.refresh_com_ports()

    def handle_text_changed(self):
        print(self.serial_communication_tab.text_area.toPlainText())

    def init_ui(self):
        self.setWindowTitle('ADCS GUI')
        self.setMinimumSize(800, 600)
        self.setGeometry(0, 0, 1270, 720)
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    window = MainWindow()
    app.exec()
