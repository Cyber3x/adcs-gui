from abc import ABC, abstractmethod
from typing import Callable, TypeVar

import numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QToolButton

T = TypeVar('T')


def create_debounce_timer(debounce_time_ms: int, callback: Callable[[], None]) -> QTimer:
    debounce_timer = QTimer()
    debounce_timer.setInterval(debounce_time_ms)
    debounce_timer.setSingleShot(True)
    debounce_timer.timeout.connect(callback)
    return debounce_timer


def action_to_button(action: QAction) -> QToolButton:
    button = QToolButton()
    button.setDefaultAction(action)
    return button


def append_to_array(array: np.ndarray, value: T, max_length: int) -> np.ndarray:
    if len(array) < max_length:
        array = np.append(array, value)
    else:
        array = np.roll(array, -1)
        array[-1] = value
    return array


def custom_JSON_encoder(obj):
    if hasattr(obj, 'reprJSON'):
        return obj.reprJSON()
    else:
        return obj


class Serializable(ABC):
    @abstractmethod
    def reprJSON(self):
        pass


def clamp(value, _min, _max):
    return max(_min, min(value, _max))


def int_or_float_to_str(value):
    """
    This function converts a float to a string and removes the decimal point and zero if the value is a whole number
    @param value: The number to convert to a string
    @return: String representation of the number
    """
    s = str(value)
    return s.replace('.0', '') if value == int(value) else s
