from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from stores.GlobalStore import State


class DebugInfoTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.state = State.get_instance()

        self.layout_main = QVBoxLayout()
        self.layout_main.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.total_packets_read_label = QLabel("Packets recieved: 0")
        self.layout_main.addWidget(self.total_packets_read_label)
        self.state.total_packets_read.add_callback(
            lambda x: self.total_packets_read_label.setText(f"Packets recieved: {x}")
        )

        self.num_of_skipped_packets_label = QLabel("Skipped packets: 0")
        self.layout_main.addWidget(self.num_of_skipped_packets_label)
        self.state.skipped_packets.add_callback(
            lambda x: self.num_of_skipped_packets_label.setText(f"Skipped packets: {x}")
        )

        self.last_data_delay_label = QLabel("Average data delay: 0ms")
        self.layout_main.addWidget(self.last_data_delay_label)
        self.state.average_data_delay.add_callback(
            lambda x: self.last_data_delay_label.setText(f"Average data delay: {x}ms")
        )

        self.min_data_delay_label = QLabel("Min data delay: 0ms")
        self.layout_main.addWidget(self.min_data_delay_label)
        self.state.min_data_delay.add_callback(lambda x: self.min_data_delay_label.setText(f"Min data delay: {x}ms"))

        self.max_data_delay_label = QLabel("Max data delay: 0ms")
        self.layout_main.addWidget(self.max_data_delay_label)
        self.state.max_data_delay.add_callback(lambda x: self.max_data_delay_label.setText(f"Max data delay: {x}ms"))

        self.setLayout(self.layout_main)
