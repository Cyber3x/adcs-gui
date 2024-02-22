import time

from PyQt6.QtGui import QTextCursor
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QComboBox, QLabel, QPushButton,
                             QPlainTextEdit)

from stores.GlobalStore import State
from utils.parsing import parse_input_line


class SerialCommunicationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.state = State()

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

        self.serial_port: QSerialPort = QSerialPort()

        self.data = bytearray()

    def refresh_com_ports(self):
        print("Refreshing COM Ports")

        self.com_port_dropdown.clear()

        # get list of available ports
        available_ports: list[QSerialPortInfo] = QSerialPortInfo.availablePorts()

        found = False
        for port in available_ports:
            self.com_port_dropdown.addItem(port.portName())

            if port.portName() == "rfcomm0":
                self.com_port_dropdown.setCurrentText("rfcomm0")
                found = True

        if found:
            time.sleep(0.5)
            self.open_port()

    def open_port(self):
        port_name = self.com_port_dropdown.currentText()

        if not port_name:
            print("No port selected")
            self.text_area.appendPlainText("No port selected")
            return

        print("Opening Port")
        if self.serial_port.isOpen():
            print(f"Port is already open, baud: {self.serial_port.baudRate()}")
            self.serial_port.close()
            print("Port closed")
            return

        # Set up serial port
        baud_rate = int(self.baud_rate_dropdown.currentText())
        data_bits = int(self.data_bits_dropdown.currentText())
        stop_bits = float(self.stop_bits_dropdown.currentText())

        self.serial_port.setPortName(port_name)
        self.serial_port.setBaudRate(baud_rate)
        self.serial_port.setDataBits(QSerialPort.DataBits(data_bits))
        self.serial_port.setStopBits(QSerialPort.StopBits(stop_bits))
        self.serial_port.setParity(QSerialPort.Parity.NoParity)
        self.serial_port.setFlowControl(QSerialPort.FlowControl.NoFlowControl)

        if self.serial_port.open(QSerialPort.OpenModeFlag.ReadWrite):
            print("Port opened")
            self.text_area.clear()
            self.text_area.appendPlainText("Port opened")
            self.serial_port.readyRead.connect(self.read_data)

            # clear data
            self.data = bytearray()
        else:
            self.text_area.appendPlainText("Port failed to open")
            print("Port failed to open")

    def read_data(self):
        # accumulate new data to the old one
        self.data += self.serial_port.readAll().data()
        lines = self.data.split(b"\n")

        # Process all complete lines
        # Ignore the last line as it might be incomplete
        for line_bytes in lines[:-1]:
            line = parse_input_line(line_bytes, self.state)

            if not line:
                continue

            self.update_text_area(line)

        # Keep the incomplete line for the next iteration
        self.data = lines[-1]

    def write_data(self, data: str):
        if self.serial_port.isOpen():
            self.serial_port.writeData(data.encode() + b'\r')
            isDataWritten = self.serial_port.flush()
            if isDataWritten:
                print("Data written")
            else:
                print("Data not written")
        else:
            print("No port is open")

    def update_text_area(self, text):
        self.text_area.appendPlainText(text)
        self.text_area.moveCursor(QTextCursor.MoveOperation.End)

        self.parent.raw_data_tab.text_area.appendPlainText(text)
        self.parent.raw_data_tab.text_area.moveCursor(QTextCursor.MoveOperation.End)

    def close_port(self):
        if self.serial_port.isOpen():
            self.serial_port.close()
            self.text_area.appendPlainText("Port closed")
            self.text_area.moveCursor(QTextCursor.MoveOperation.End)
        else:
            self.text_area.appendPlainText("No port is open")
