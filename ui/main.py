import sys
from enum import Enum
from random import choice, randint

from PyQt6.QtCore import QPoint, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QLineEdit,
)


class State(Enum):
    WALK = 0
    HISS = 1
    FIGHT = 2


state2color = {0: "green", 1: "orange", 2: "red"}


class DrawDots(QWidget):
    def __init__(self, n):
        super().__init__()
        self.cats_num = n

        self.coordinates = [
            [randint(0, 750) for _ in range(n)],
            [randint(0, 1000) for _ in range(n)],
        ]
        self.states = [QColor(state2color[choice(list(State)).value]) for _ in range(n)]

        # Set up a timer to update positions
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_positions)
        self.timer.start(100)

    def paintEvent(self, event):
        # Create a QPainter object to perform the drawing
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(10)
        painter.setPen(pen)

        for i in range(self.cats_num):
            pen.setColor(self.states[i])
            painter.setPen(pen)
            painter.drawPoint(QPoint(self.coordinates[0][i], self.coordinates[1][i]))

    def update_positions(self):
        # Update the position of each dot randomly
        for i in range(self.cats_num):
            # Randomly change the position of each dot
            x_offset = randint(-10, 10)  # Random offset for x
            y_offset = randint(-10, 10)  # Random offset for y

            # Update the dot's position
            new_x = self.coordinates[0][i] + x_offset
            new_y = self.coordinates[1][i] + y_offset

            # Keep the dots within the widget's bounds
            new_x = max(0, min(new_x, self.width()))  # Keep within bounds
            new_y = max(0, min(new_y, self.height()))  # Keep within bounds

            self.coordinates[0][i] = new_x
            self.coordinates[1][i] = new_y

        self.update()  # Trigger a repaint


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.setWindowTitle("Cats")
        self.setMinimumSize(1000, 1000)  # Set a minimum size for the window

        self.input_field = QLineEdit()
        self.input_field.setMaximumWidth(250)
        self.input_field.setPlaceholderText("Enter number of cats")
        self.input_field.returnPressed.connect(
            self.start_dots
        )  # Use returnPressed signal

        # Initially, no dots widget is created
        self.dots = None

        # Add the QLineEdit and an empty widget placeholder for DrawDots
        self.layout.addWidget(self.input_field)

        # Create a central widget and set the layout
        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

    def start_dots(self):
        # Get the number from the QLineEdit
        num = self.input_field.text()

        if num.isdigit():  # Ensure the input is a valid number
            num = int(num)

            # If there is already a dots widget, remove it
            if self.dots is not None:
                self.layout.removeWidget(self.dots)
                self.dots.deleteLater()  # Properly delete the old widget

            # Create a new instance of DrawDots with the specified number of dots
            self.dots = DrawDots(num)
            self.layout.addWidget(self.dots)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
