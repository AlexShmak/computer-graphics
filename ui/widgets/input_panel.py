from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)


class InputPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.input_fields = InputFields()
        self.number = self.input_fields.input_number
        self.radius = self.input_fields.input_radius
        self.r0 = self.input_fields.input_r0
        self.r1 = self.input_fields.input_r1

        # Create a frame for the input layout
        self.input_frame = QFrame(self)
        self.input_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.input_frame.setFrameShadow(QFrame.Shadow.Raised)

        self.input_layout = QVBoxLayout(self.input_frame)
        self.input_layout.setAlignment(Qt.AlignCenter)

        self.input_layout.addWidget(self.input_fields.input_number_label)
        self.input_layout.addWidget(self.input_fields.input_number)

        self.input_layout.addWidget(self.input_fields.input_radius_label)
        self.input_layout.addWidget(self.input_fields.input_radius)

        self.input_layout.addWidget(self.input_fields.input_r1_label)
        self.input_layout.addWidget(self.input_fields.input_r1)

        self.input_layout.addWidget(self.input_fields.input_r0_label)
        self.input_layout.addWidget(self.input_fields.input_r0)


class InputFields(QWidget):
    def __init__(self):
        super().__init__()

        # Add labels for input fields
        self.input_number_label = QLabel("Number of cats")
        self.input_number_label.setAlignment(Qt.AlignCenter)

        self.input_radius_label = QLabel("Maximum travel radius")
        self.input_radius_label.setAlignment(Qt.AlignCenter)

        self.input_r0_label = QLabel("Cats start fighting at a distance:")
        self.input_r0_label.setAlignment(Qt.AlignCenter)

        self.input_r1_label = QLabel("Cats start hissing at a distance:")
        self.input_r1_label.setAlignment(Qt.AlignCenter)

        # Set the input field for getting number of cats
        self.input_number = QLineEdit()
        self.input_number.setMaximumWidth(250)
        self.input_number.setPlaceholderText("Enter number of cats")

        # Set the input field for getting radius
        self.input_radius = QLineEdit()
        self.input_radius.setMaximumWidth(250)
        self.input_radius.setPlaceholderText("Enter travel radius")

        # Set the input field for getting hissing distance
        self.input_r1 = QLineEdit()
        self.input_r1.setMaximumWidth(250)
        self.input_r1.setPlaceholderText("Enger hissing distance")

        # Set the input field for getting fighting distance
        self.input_r0 = QLineEdit()
        self.input_r0.setMaximumWidth(250)
        self.input_r0.setPlaceholderText("Enter fighting distance")
