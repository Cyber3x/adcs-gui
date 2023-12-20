from PyQt6.QtWidgets import QFrame
from typing import Union, Literal

Shape = Union[Literal['horizontal'], Literal['vertical']]


class SeparatorLine(QFrame):
    def __init__(self, shape: Shape):
        super().__init__()
        self.setFrameShape(shape == 'horizontal' and QFrame.Shape.HLine or QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
