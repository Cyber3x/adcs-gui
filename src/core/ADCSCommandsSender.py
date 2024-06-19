import logging

from .SingletonMeta import Singelton
from .SerialManager import SerialManager

log = logging.getLogger()


@Singelton
class ADCSCommandsSender:
    def __init__(self):
        self.serial_manager = SerialManager.get_instance()

        # TODO: info for motor pwn, should be moved to some settings
        self.pwn_prescale = 0
        self.period = 50_000

    def imu_start_reading(self):
        if not self.serial_manager.is_port_open():
            log.debug("Can send command, now serial opet is open")
            return False

        self.serial_manager.write_data("imu start")

    def imu_stop_reading(self):
        if not self.serial_manager.is_port_open():
            log.debug("Can send command, now serial opet is open")
            return False

        self.serial_manager.write_data("imu stop")

    def set_stepper(self, stepper_index: int, move_amount: float):
        if not self.serial_manager.is_port_open():
            log.debug("Can send command, now serial opet is open")
            return False

        if stepper_index < 0 or stepper_index > 2:
            raise "Stepper index out of bounds"

        if move_amount < 0 or move_amount > 100:
            raise f"move_ammount {move_amount} is not an allowed value, should be a value between [0, 100]"

        self.serial_manager.write_data(f"stepper {stepper_index} move {move_amount}")

    def set_motor_speed(self, dc_motor_index: int, speed_percentage: float):
        if not self.serial_manager.is_port_open():
            log.debug("Can send command, now serial opet is open")
            return False

        if dc_motor_index < 0 or dc_motor_index > 2:
            raise "DC motor index out of bounds"

        if speed_percentage < -100 or speed_percentage > 100:
            raise f"Speed percentage out of bounds"

        speed_percentage /= 100
        """
        `pwm [duty|period|prescale] [...]`
        * Adjust PWM-related settings.
        * Used PWM channels are 1, 3 and 4 
        * Options:
          - `duty [n] [c]` - set duty cycle of channel [c] to n/65536 [0 <= n <= 65535]
          - `period [n]` - set period to [n] [0 <= n <= 65535]
          - `prescale [n]` - set prescale to [n] [1 <= n <= 65535]
          """
        self.serial_manager.write_data(f"pwm duty {dc_motor_index} {self.period * speed_percentage}")

    def stop_motor(self, dc_motor_index: int):
        if not self.serial_manager.is_port_open():
            log.debug("Can send command, now serial opet is open")
            return False

        if dc_motor_index < 0 or dc_motor_index > 2:
            raise "DC motor index out of bounds"

        self.serial_manager.write_data(f"pwm duty {dc_motor_index} 0")
