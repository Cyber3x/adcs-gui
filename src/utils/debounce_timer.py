from PyQt6.QtCore import QTimer
from typing import Callable


def create_debounce_timer(debounce_time_ms: int, callback: Callable[[], None]) -> QTimer:
    debounce_timer = QTimer()
    debounce_timer.setInterval(debounce_time_ms)
    debounce_timer.setSingleShot(True)
    debounce_timer.timeout.connect(callback)
    return debounce_timer
