from typing import Dict

from core.ObservableValue import create_observable_value, ObservableValue


class State:
    _instance = None

    stepper_values: Dict[str, ObservableValue] = {
        "X": create_observable_value(0, "stepper_value_X"),
        "Y": create_observable_value(0, "stepper_value_Y"),
        "Z": create_observable_value(0, "stepper_value_Z"),
    }

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(State, cls).__new__(cls, *args, **kwargs)
        return cls._instance
