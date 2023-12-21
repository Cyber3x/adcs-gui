from PyQt6.QtGui import QIntValidator


class IntValidator(QIntValidator):

    def __init__(self, min_value: int = -360, max_value: int = 360):
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value

    def fixup(self, input_str):
        return input_str

    def validate(self, input_str, pos):
        if input_str == "" or (input_str == "-" and self.min_value < 0):
            return QIntValidator.State.Acceptable, input_str, pos
        try:
            value = int(input_str)
            if value < self.min_value or value > self.max_value:
                return QIntValidator.State.Invalid, input_str, pos
            else:
                return QIntValidator.State.Acceptable, input_str, pos
        except ValueError:
            return QIntValidator.State.Invalid, input_str, pos
