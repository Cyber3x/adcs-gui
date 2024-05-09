import logging
import time

import zope.interface

from core import ISerialDataListener

log = logging.getLogger()


@zope.interface.implementer(ISerialDataListener)
class SerialSpeedTester:
    last_temp_time = None
    last_number = None
    num_of_skipped_packets = 0

    def on_new_line(self, line: str):
        if line.startswith("temp"):
            if self.last_temp_time is None:
                self.last_temp_time = time.time_ns()
                return

            current_time = time.time_ns()
            delta_ns = current_time - self.last_temp_time
            delta_ms = delta_ns / 1E6  # num of ns in ms
            log.debug(f"Data delta: {delta_ms}")
            self.last_temp_time = current_time


        elif line.startswith("counter"):
            number = int(line[len("counter "):])
            if self.last_number is None:
                self.last_number = number
                return

            if number == self.last_number + 1:
                log.debug("good packet")
            else:
                self.num_of_skipped_packets += 1
                log.debug(f"skipped packet, in total: {self.num_of_skipped_packets}")

            self.last_number = number
