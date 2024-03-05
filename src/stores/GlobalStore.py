from typing import Dict, List, Callable, Literal, Optional

import numpy as np
from jsonschema import validate, ValidationError

from core.ObservableValue import create_observable_value
from utils.utils import append_to_array
from validators.schemas import stepper_values_schema

# custom types
Axis = Literal["X", "Y", "Z"]
Axes = List[Axis]
IMU_Data_Dict = Dict[Axis, np.ndarray]

axes: Axes = ["X", "Y", "Z"]

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


class StepperValues:
    def __init__(self):
        self.X = create_observable_value(0, "stepper_value_X")
        self.Y = create_observable_value(0, "stepper_value_Y")
        self.Z = create_observable_value(0, "stepper_value_Z")

    def reprJSON(self):
        return {
            "stepper_values": {
                "X": self.X,
                "Y": self.Y,
                "Z": self.Z,
            }
        }

    # TODO: should we validate the data before every update?
    # could this be a performance hit? for now probably not but something to thing about
    # TODO: if the motors can't move in parallel we need too add delay in order to move them sequentially

    def update(self, new_data: str) -> Optional[ValidationError]:
        """
        Update the stepper values from a json string

        :param new_data: a json string with the stepper values

        :return: None if the data is valid, ValidationError if the data is invalid
        """

        try:
            validate(new_data, stepper_values_schema)
        except ValidationError as e:
            return e

        self.X.set(new_data["stepper_values"]["X"])
        self.Y.set(new_data["stepper_values"]["Y"])
        self.Z.set(new_data["stepper_values"]["Z"])


class DCMotorValues:
    MAX_ANGULAR_VELOCITY = 2  # rads/sec
    MIN_ANGULAR_VELOCITY = -2  # rads/sec

    def __init__(self):
        self.angular_velocity_control = {
            "tuning_paramiters": {
                "P": create_observable_value(0, "angular_velocity_P"),
                "I": create_observable_value(0, "angular_velocity_I"),
                "D": create_observable_value(0, "angular_velocity_D"),
            },
            "values": {
                # in rads/sec
                "X": create_observable_value(0, "angular_velocity_X"),
                "Y": create_observable_value(2, "angular_velocity_Y"),
                "Z": create_observable_value(0, "angular_velocity_Z"),
            }
        }

        self.angle_control = {
            "tuning_paramiters": {
                "P": create_observable_value(0, "angle_P"),
                "I": create_observable_value(0, "angle_I"),
                "D": create_observable_value(0, "angle_D"),
            },
            "values": {
                # in rads
                "X": create_observable_value(0, "angle_X"),
                "Y": create_observable_value(0, "angle_Y"),
                "Z": create_observable_value(0, "angle_Z"),
            }
        }


class State:
    _instance = None

    stepper_values = StepperValues()
    dc_motor_values = DCMotorValues()

    # The length of the IMU data history in milliseconds
    # So here 2000ms = 2s of data will be displayed on graphs
    # TODO: this can be changed in a config
    # watch out that when the time shrinks the np array needs to be resized
    IMU_data_history_length_ms = 5000

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
