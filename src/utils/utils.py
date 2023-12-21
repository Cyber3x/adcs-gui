from typing import Callable, TypeVar

import numpy as np
from PyQt6.QtCore import QTimer

T = TypeVar('T')


def create_debounce_timer(debounce_time_ms: int, callback: Callable[[], None]) -> QTimer:
    debounce_timer = QTimer()
    debounce_timer.setInterval(debounce_time_ms)
    debounce_timer.setSingleShot(True)
    debounce_timer.timeout.connect(callback)
    return debounce_timer


def append_to_array(array: np.ndarray, value: T, max_length: int) -> np.ndarray:
    if len(array) < max_length:
        array = np.append(array, value)
    else:
        array = np.roll(array, -1)
        array[-1] = value
    return array
