import logging

import zope.interface

from core import ISerialDataListener
from stores.GlobalStore import State

log = logging.getLogger()


def extract_numbers(line: str):
    useful_numbers = line[line.index("(") + 1:line.index(")")]
    return list(map(float, useful_numbers.split(",")))


@zope.interface.implementer(ISerialDataListener)
class SerialDataParser:
    def __init__(self):
        self.store = State.get_instance()

    def on_new_line(self, line: str):
        if line.startswith("counter"):
            number = int(line[len("counter "):])
            self.store.add_packet_number(number)

        elif line.startswith("acc"):
            self.store.add_IMU_acceleration_datapoint(*extract_numbers(line))

        elif line.startswith("gyro"):
            self.store.add_IMU_gyroscope_datapoint(*extract_numbers(line))

        elif line.startswith("angle"):
            self.store.add_IMU_angle_datapoint(*extract_numbers(line))

        elif line.startswith("temp"):
            self.store.add_IMU_temperature_datapoint(float(line[len("temp"):]))

        else:
            log.warning("unknown data for parsing: " + line)
