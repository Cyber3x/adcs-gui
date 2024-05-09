import logging

from PyQt6.QtGui import QTextCursor
from PyQt6.QtSerialPort import QSerialPortInfo
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QLabel, QPushButton,
    QPlainTextEdit)
from zope.interface import implementer

from core import SerialManager, ISerialDataListener
from stores.GlobalStore import State

log = logging.getLogger()


@implementer(ISerialDataListener)
class SerialCommunicationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.state = State.get_instance()
        self.serial_manager = SerialManager.get_instance()
        self.serial_manager.add_listener(self)

        # Create a layout for the serial communication tab
        self.serial_layout = QVBoxLayout(self)

        self.serial_layout.addWidget(QLabel("Settings"))

        # Refresh COM Ports button
        self.refresh_button = QPushButton("Refresh COM Ports")
        self.serial_layout.addWidget(self.refresh_button)
        self.refresh_button.clicked.connect(self.refresh_com_ports)

        # COM Port dropdown
        self.com_port_dropdown = QComboBox()
        self.serial_layout.addWidget(QLabel("COM Port:"))
        self.serial_layout.addWidget(self.com_port_dropdown)

        # ----- PORT SETTINGS LAYOUT -----
        self.layout_port_settings = QHBoxLayout()

        # Baud Rate dropdown
        self.baud_rate_dropdown = QComboBox()
        self.layout_port_settings.addWidget(QLabel("Baud Rate:"))
        self.layout_port_settings.addWidget(self.baud_rate_dropdown)

        # Set up the baud rate options
        # baud_rates = QSerialPortInfo.standardBaudRates()
        # baud_rates = QSerialPort.BaudRate
        baud_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        self.baud_rate_dropdown.addItems(map(str, baud_rates))
        self.baud_rate_dropdown.setCurrentIndex(baud_rates.index(115200))

        # setup data bits options
        data_bits = [5, 6, 7, 8]
        self.data_bits_dropdown = QComboBox()
        self.layout_port_settings.addWidget(QLabel("Data Bits:"))
        self.layout_port_settings.addWidget(self.data_bits_dropdown)
        self.data_bits_dropdown.addItems(map(str, data_bits))
        self.data_bits_dropdown.setCurrentText("8")  # Set default to 8 bits

        # setup stop bits options
        stop_bits = [1, 2]

        self.stop_bits_dropdown = QComboBox()
        self.stop_bits_dropdown.addItems(map(str, stop_bits))
        self.stop_bits_dropdown.setCurrentText("1")  # Set default to 1 stop bit
        q_label = QLabel("Stop Bits:")
        # q_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.layout_port_settings.addWidget(q_label)
        self.layout_port_settings.addWidget(self.stop_bits_dropdown)

        self.serial_layout.addLayout(self.layout_port_settings)
        # ----- END OF PORT SETTINGS LAYOUT -----

        # Open port button
        self.open_button = QPushButton("Open Port")
        self.serial_layout.addWidget(self.open_button)
        self.open_button.clicked.connect(self.open_port)

        # Close port button
        self.close_button = QPushButton("Close Port")
        self.serial_layout.addWidget(self.close_button)
        self.close_button.clicked.connect(self.close_port)

        # Raw data text area
        self.text_area = QPlainTextEdit()
        self.serial_layout.addWidget(QLabel("Received Data:"))
        self.serial_layout.addWidget(self.text_area)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.text_area.clear)
        self.serial_layout.addWidget(self.clear_button)

        self.setLayout(self.serial_layout)

    def refresh_com_ports(self):
        log.debug("Refresing com ports")

        self.com_port_dropdown.clear()

        # get list of available ports
        available_ports: list[QSerialPortInfo] = self.serial_manager.get_available_ports()

        # try to find rfcomm0, if successful open it, else wait for the user
        found = False
        for port in available_ports:
            self.com_port_dropdown.addItem(port.portName())

            if port.portName() == "rfcomm0":
                self.com_port_dropdown.setCurrentText("rfcomm0")
                found = True

    def open_port(self):
        port_name = self.com_port_dropdown.currentText()

        if not port_name:
            log.debug("No port selected")
            self.text_area.appendPlainText("No port selected")
            return

        # Set up serial port
        baud_rate = int(self.baud_rate_dropdown.currentText())
        data_bits = int(self.data_bits_dropdown.currentText())
        stop_bits = float(self.stop_bits_dropdown.currentText())

        opened = self.serial_manager.open_port(port_name, baud_rate, data_bits, stop_bits)

        if opened:
            self.text_area.clear()
            self.text_area.appendPlainText("Port opened")
            self.serial_manager.start_reading()
            log.debug("Port opened: " + port_name)
        else:
            self.text_area.appendPlainText("Port failed to open")
            log.debug("Failed to open serial port: " + port_name)

    def update_text_area(self, text):
        self.text_area.appendPlainText(text)
        self.text_area.moveCursor(QTextCursor.MoveOperation.End)

        self.parent.raw_data_tab.text_area.appendPlainText(text)
        self.parent.raw_data_tab.text_area.moveCursor(QTextCursor.MoveOperation.End)

    def close_port(self):
        closed = self.serial_manager.close_port()

        if closed:
            self.text_area.appendPlainText("Port closed")
            self.text_area.moveCursor(QTextCursor.MoveOperation.End)
        else:
            self.text_area.appendPlainText("No port is open")

    def on_new_line(self, line: str):
        self.update_text_area(line)
