import logging
import math
import time
from typing import Dict, List, Callable, Literal

import numpy as np

from core.ObservableValue import create_observable_value
from core.SingletonMeta import Singelton
from utils.utils import Serializable
from utils.utils import append_to_array

# custom types
Axis = Literal["X", "Y", "Z"]
Axes = List[Axis]
IMU_Data_Dict = Dict[Axis, np.ndarray]

axes: Axes = ["X", "Y", "Z"]

# TODO: move this to some settings state
# there's a default value but it can be changed wiht a command
data_interval_delay_ms = 50

MAX_ANGULAR_VELOCITY = 100  # percent
MIN_ANGULAR_VELOCITY = -100  # percent

log = logging.getLogger()


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


class AxisData(Serializable):
    """
    A generic class to store data related to each axis

    :param name: the name of the data, used to create the observable values and when saving the data to json
    """

    def __init__(self, name: str):
        self.name = name
        self.X = create_observable_value(0, f"{name}_X")
        self.Y = create_observable_value(0, f"{name}_Y")
        self.Z = create_observable_value(0, f"{name}_Z")

    def update(self, new_data: str):
        self.X.set(new_data[self.name]["X"])
        self.Y.set(new_data[self.name]["Y"])
        self.Z.set(new_data[self.name]["Z"])

    def reprJSON(self):
        return {
            self.name: {
                "X": self.X,
                "Y": self.Y,
                "Z": self.Z,
            }
        }


class StepperValues(Serializable):
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

    def update(self, new_data: str):
        self.X.set(new_data["stepper_values"]["X"])
        self.Y.set(new_data["stepper_values"]["Y"])
        self.Z.set(new_data["stepper_values"]["Z"])


class PIDParametersData(Serializable):
    """
    This calss is used to store the PID values. Used as a data class
    """

    def __init__(self, name: str):
        self.name = name
        self.P = create_observable_value(0, f"{name}_P")
        self.I = create_observable_value(0, f"{name}_I")
        self.D = create_observable_value(0, f"{name}_D")

    def reprJSON(self):
        return {
            self.name: {
                "P": self.P,
                "I": self.I,
                "D": self.D,
            }
        }

    def update(self, new_data: str):
        self.P.set(new_data[self.name]["P"])
        self.I.set(new_data[self.name]["I"])
        self.D.set(new_data[self.name]["D"])

    def __str__(self):
        return f"PIDParametersData({self.name}) - P: {self.P.get()} I: {self.I.get()} D: {self.D.get()}"


class DCMotorValues:
    def __init__(self):
        self.angular_velocity_control = {
            "PIDParams": PIDParametersData("PID_values_angular_velocity_control"),
            "values": AxisData("angular_velocity")  # rads/sec
        }

        self.angle_control = {
            "PIDParams": PIDParametersData("PID_values_angle_control"),
            "values": AxisData("angle")  # rads
        }


@Singelton
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

    # Debug information
    average_data_delay = create_observable_value(0)
    min_data_delay = create_observable_value(math.inf)
    max_data_delay = create_observable_value(-math.inf)
    total_packets_read = create_observable_value(0)
    skipped_packets = create_observable_value(0)
    _sum_data_delay = 0

    # settings
    is_output_raw_data = create_observable_value(True)

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
        self.IMU_temperature_data.data = append_to_array(
            self.IMU_temperature_data.data, temp,
            self.IMU_max_number_of_datapoints
        )

        for callback in self.IMU_temperature_data.get_callbacks():
            callback(self.IMU_temperature_data.data)

    last_packet_number = None
    last_packet_time = None

    def add_packet_number(self, packet_number: int):
        self.total_packets_read.set(self.total_packets_read.get() + 1)

        if self.last_packet_number is not None and self.last_packet_number + 1 != packet_number:
            self.skipped_packets.set(self.skipped_packets.get() + 1)

        now_ns = time.time_ns()
        if self.last_packet_time is not None:
            delay_ns = now_ns - self.last_packet_time
            delay_ms = delay_ns / 1_000_000
            self._sum_data_delay += delay_ms
            self.average_data_delay.set(self._sum_data_delay / self.total_packets_read.get())
            if self.total_packets_read.get() > 50:
                self.min_data_delay.set(min(delay_ms, self.min_data_delay.get()))
                self.max_data_delay.set(max(delay_ms, self.max_data_delay.get()))
            # print(delay_ms)

        self.last_packet_time = now_ns

        self.last_packet_number = packet_number

    def __init__(self):
        log.info("GLoablStore - constructor called")
