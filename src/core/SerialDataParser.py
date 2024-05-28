import logging
import time

import zope.interface

from core import ISerialDataListener
from stores.GlobalStore import State
from collections import deque

log = logging.getLogger()


def extract_numbers(line: str):
    start = line.index("(") + 1
    end = line.index(")")
    return [float(x) for x in line[start:end].split(",")]


@zope.interface.implementer(ISerialDataListener)
class SerialDataParser:
    def __init__(self):
        self.store = State.get_instance()
        self.line_queue = deque()
        # self.last = None

    def on_new_line(self, line: str):
        self.line_queue.append(line)
        self.process_queue()

    def process_queue(self):
        while self.line_queue:
            line = self.line_queue.popleft()
            if line.startswith("counter"):
                number = int(line[8:])
                self.store.add_packet_number(number)
                # now = time.time_ns()
                #
                # if self.last:
                #     delta = now - self.last
                #
                # self.last = now

            elif line.startswith("acc"):
                self.store.add_IMU_acceleration_datapoint(*extract_numbers(line))

            elif line.startswith("gyro"):
                self.store.add_IMU_gyroscope_datapoint(*extract_numbers(line))

            elif line.startswith("angle"):
                self.store.add_IMU_angle_datapoint(*extract_numbers(line))

            elif line.startswith("temp"):
                self.store.add_IMU_temperature_datapoint(float(line[5:]))

            else:
                log.warning("unknown data for parsing: " + line)
