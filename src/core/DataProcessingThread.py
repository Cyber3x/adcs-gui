import threading
import time
from collections import deque
from PyQt6.QtCore import QThread
from core.SerialDataParser import SerialDataParser


class DataProcessingThread(QThread):
    def __init__(self):
        super().__init__()
        self.parser = SerialDataParser()
        self.line_queue = deque()
        self.lock = threading.Lock()
        self.running = True

    def run(self):
        while self.running:
            with self.lock:
                if self.line_queue:
                    line = self.line_queue.popleft()
                else:
                    line = None

            if line:
                self.parser.process_line(line)

            time.sleep(0.01)  # Sleep briefly to reduce CPU usage

    def add_line(self, line: str):
        with self.lock:
            self.line_queue.append(line)

    def stop(self):
        self.running = False
        self.wait()  # Wait for the thread to finish
