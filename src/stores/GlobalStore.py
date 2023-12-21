from typing import Dict, List, Callable, Literal

import numpy as np

from core.ObservableValue import create_observable_value, ObservableValue
from utils.utils import append_to_array

# custom types
Axis = Literal["X", "Y", "Z"]
IMU_Data_Dict = Dict[Axis, np.ndarray]

axes: List[Axis] = ["X", "Y", "Z"]

# TODO: move this to some settings state
# there's a default value but it can be changed wiht a command
data_interval_delay_ms = 50


class IMUData:
    def __init__(self):
        self.data: IMU_Data_Dict = {
            "X": np.zeros(0),
            "Y": np.zeros(0),
            "Z": np.zeros(0),
        }
        self._callbacks: List[Callable[[IMU_Data_Dict], None]] = []

    def add_callback(self, callback: Callable[[IMU_Data_Dict], None]):
        self._callbacks.append(callback)

    def get_callbacks(self):
        return self._callbacks


class IMUDataTemperature:
    def __init__(self):
        self.data: np.ndarray = np.zeros(0)
        self._callbacks: List[Callable[[np.ndarray], None]] = []

    def add_callback(self, callback: Callable[[np.ndarray], None]):
        self._callbacks.append(callback)

    def get_callbacks(self):
        return self._callbacks


class State:
    _instance = None

    stepper_values: Dict[Axis, ObservableValue] = {
        "X": create_observable_value(0, "stepper_value_X"),
        "Y": create_observable_value(0, "stepper_value_Y"),
        "Z": create_observable_value(0, "stepper_value_Z"),
    }

    # The length of the IMU data history in milliseconds
    # So here 2000ms = 2s of data will be displayed on graphs
    # TODO: this can be changed in a config
    # watch out that when the time shrinks the np array needs to be resized
    IMU_data_history_length_ms = 2000

    IMU_max_number_of_datapoints = int(IMU_data_history_length_ms / data_interval_delay_ms)

    IMU_angle_data = IMUData()
    IMU_acceleration_data = IMUData()
    IMU_gyroscope_data = IMUData()
    IMU_magnetometer_data = IMUData()

    IMU_temperature_data = IMUDataTemperature()

    def _add_IMU_datapoint(self, IMU_data: IMUData, x: float, y: float, z: float):
        for axis in axes:
            IMU_data.data[axis] = append_to_array(
                IMU_data.data[axis],
                locals()[axis.lower()],  # returns a dict with keys IMU_data, x, y and z which are the fucntion params
                self.IMU_max_number_of_datapoints
            )

        for callback in IMU_data.get_callbacks():
            callback(IMU_data.data)

    def add_IMU_angle_datapoint(self, x: float, y: float, z: float):
        self._add_IMU_datapoint(self.IMU_angle_data, x, y, z)

    def add_IMU_acceleration_datapoint(self, x: float, y: float, z: float):
        self._add_IMU_datapoint(self.IMU_acceleration_data, x, y, z)

    def add_IMU_gyroscope_datapoint(self, x: float, y: float, z: float):
        self._add_IMU_datapoint(self.IMU_gyroscope_data, x, y, z)

    def add_IMU_magnetometer_datapoint(self, x: float, y: float, z: float):
        self._add_IMU_datapoint(self.IMU_magnetometer_data, x, y, z)

    def add_IMU_temperature_datapoint(self, temp: float):
        self.IMU_temperature_data.data = append_to_array(self.IMU_temperature_data.data, temp,
                                                         self.IMU_max_number_of_datapoints)

        for callback in self.IMU_temperature_data.get_callbacks():
            callback(self.IMU_temperature_data.data)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(State, cls).__new__(cls, *args, **kwargs)
        return cls._instance
