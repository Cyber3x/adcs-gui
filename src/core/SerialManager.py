import logging

from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo

from core.ISerialDataListener import ISerialDataListener
from core.ISubject import ISubject
from core.SingletonMeta import Singelton

log = logging.getLogger()


@Singelton
class SerialManager(ISubject[ISerialDataListener]):
    def __init__(self):
        super().__init__()
        self.serial_port = QSerialPort()
        self.data = bytearray()

        self.data_listeners: list[ISerialDataListener] = []
        log.info("SerialManager - constructor called")

    @staticmethod
    def get_available_ports():
        return QSerialPortInfo.availablePorts()

    def open_port(self, port_name: str, baud_date: int, data_bits: int, stop_bits: float):
        log.debug("Opening port: " + port_name)
        if self.serial_port.isOpen():
            log.warning(f"Serial port was already open ({port_name}), closing the connection")
            self.serial_port.close()

        self.serial_port.setPortName(port_name)
        self.serial_port.setBaudRate(baud_date)
        self.serial_port.setDataBits(QSerialPort.DataBits(data_bits))
        self.serial_port.setStopBits(QSerialPort.StopBits(stop_bits))
        self.serial_port.setParity(QSerialPort.Parity.NoParity)
        self.serial_port.setFlowControl(QSerialPort.FlowControl.NoFlowControl)

        return self.serial_port.open(QSerialPort.OpenModeFlag.ReadWrite)

    def start_reading(self):
        if not self.serial_port.isOpen():
            log.error("Tried to start reading while no serial port was open")
            return

        self.serial_port.readyRead.connect(self.reader)

    # an observer that will read data from the serial plot
    def reader(self):
        # accumulate new data to the old one
        self.data += self.serial_port.readAll().data()
        lines = self.data.split(b"\n")

        # Process all complete lines
        # Ignore the last line as it might be incomplete
        for line_bytes in lines[:-1]:
            try:
                line = line_bytes.decode().strip()
                self.notify_listeners(line)
            except UnicodeDecodeError:
                log.error("UnicodeDecodeError for line: " + line_bytes)
                continue

            # log.info("parsed line: " + line)

        # Keep the incomplete line for the next iteration
        self.data = lines[-1]

    def write_data(self, data: str) -> bool:
        if not self.serial_port.isOpen():
            log.error("No port is open")
            return False

        self.serial_port.writeData(data.encode() + b'\r')
        is_data_written = self.serial_port.flush()

        # TODO: remove this, this is here just for debugging info
        if is_data_written:
            log.debug("Data written")
        else:
            log.warning("Data not written")

        return is_data_written

    def close_port(self) -> bool:
        """
        @return: bool - True if managed to close the port, else False
        """
        if not self.serial_port.isOpen():
            log.error("No port is open to close")
            return False

        self.serial_port.readyRead.disconnect(self.reader)
        log.debug("Closed port: " + self.serial_port.portName())
        self.serial_port.close()
        return True

    def add_listener(self, listener: ISerialDataListener):
        self.data_listeners.append(listener)

    def remove_listener(self, listener: ISerialDataListener):
        self.data_listeners.remove(listener)

    def notify_listeners(self, line):
        for l in self.data_listeners:
            l.on_new_line(line)
