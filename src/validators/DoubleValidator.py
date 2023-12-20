from PyQt6.QtGui import QDoubleValidator


class DoubleValidator(QDoubleValidator):

    def __init__(self, min_value: float = -360, max_value: float = 360, number_of_decimals: int = 2):
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value
        self.number_of_decimals = number_of_decimals

    def fixup(self, input_str):
        return input_str

    def validate(self, input_str, pos):
        if input_str == "" or input_str == "-":
            return QDoubleValidator.State.Acceptable, input_str, pos
        try:
            value = float(input_str)
            if (value < self.min_value or value > self.max_value
                    or len(input_str.split(".")[-1]) > self.number_of_decimals):
                return QDoubleValidator.State.Invalid, input_str, pos
            else:
                return QDoubleValidator.State.Acceptable, input_str, pos
        except ValueError:
            return QDoubleValidator.State.Invalid, input_str, pos
