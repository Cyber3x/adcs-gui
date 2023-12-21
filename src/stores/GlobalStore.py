from typing import Dict

import numpy as np

from core.ObservableValue import create_observable_value, ObservableValue

axes = ["X", "Y", "Z"]


class State:
    _instance = None

    stepper_values: Dict[str, ObservableValue] = {
        "X": create_observable_value(0, "stepper_value_X"),
        "Y": create_observable_value(0, "stepper_value_Y"),
        "Z": create_observable_value(0, "stepper_value_Z"),
    }

    # The length of the IMU data history in milliseconds
    # So here 2000ms = 2s of data will be displayed on graphs
    # TODO: implement this
    IMU_data_history_length_ms = 2000

    IMU_max_number_of_datapoints = 500

    IMU_acceleration_data: Dict[str, np.ndarray] = {
        "X": np.zeros(0),
        "Y": np.zeros(0),
        "Z": np.zeros(0),
    }

    IMU_gyroscope_data: Dict[str, np.ndarray] = {
        "X": np.zeros(0),
        "Y": np.zeros(0),
        "Z": np.zeros(0),
    }

    IMU_magnetometer_data: Dict[str, np.ndarray] = {
        "X": np.zeros(0),
        "Y": np.zeros(0),
        "Z": np.zeros(0),
    }

    IMU_angle_data: Dict[str, np.ndarray] = {
        "X": np.zeros(IMU_max_number_of_datapoints),
        "Y": np.zeros(IMU_max_number_of_datapoints),
        "Z": np.zeros(IMU_max_number_of_datapoints),
    }

    IMU_temperature_data: np.ndarray = np.zeros(0)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(State, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def add_IMU_angle_datapoint(self, x: float, y: float, z: float):
        self.IMU_angle_data["X"] = np.roll(self.IMU_angle_data["X"], -1)
        self.IMU_angle_data["Y"] = np.roll(self.IMU_angle_data["Y"], -1)
        self.IMU_angle_data["Z"] = np.roll(self.IMU_angle_data["Z"], -1)

        self.IMU_angle_data["X"][-1] = x
        self.IMU_angle_data["Y"][-1] = y
        self.IMU_angle_data["Z"][-1] = z

    def get_IMU_angle_data(self):
        return self.IMU_angle_data
