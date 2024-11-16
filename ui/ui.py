import sys

from PyQt6.QtCore import QPoint, QTimer
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QMainWindow,
    QWidget,
    QPushButton,
)

# ? needed when importing `generator`
sys.path.append("/home/alex/dev/uni/computer-graphics/")

from generator.generator import CatGenerator


class DrawCats(QWidget):
    def __init__(self, n, generator):
        super().__init__()
        self.cats_num = n

        self.generator = generator
        self.coordinates = generator.cats

        # Set up a timer to update positions
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_positions)
        self.timer.start(350)

    def paintEvent(self, event):
        # Create a QPainter object to perform the drawing
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(3)
        painter.setPen(pen)

        for i in range(self.cats_num):
            painter.setPen(pen)
            painter.drawPoint(
                QPoint(int(self.coordinates[0][i]), int(self.coordinates[1][i]))
            )

    def update_positions(self):
        self.generator.update_cats()
        self.coordinates = self.generator.cats

        self.update()  # Trigger another iteration of painting


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.generator = None
        self.cats_number = None
        self.radius = None

        self.layout = QHBoxLayout()
        self.left_side = QVBoxLayout()

        # Set the main window and get its geometry
        self.setWindowTitle("Cats")
        self.setMinimumSize(1000, 1000)
        self.height = self.frameGeometry().height()
        self.width = self.frameGeometry().width()

        # Set the input field for getting number of cats
        self.input_number = QLineEdit()
        self.input_number.setMaximumWidth(250)
        self.input_number.setPlaceholderText("Enter number of cats")

        # Set the input field for getting radius
        self.input_radius = QLineEdit()
        self.input_radius.setMaximumWidth(250)
        self.input_radius.setPlaceholderText("Enter travel radius")

        # Set the button to start animation
        self.start_button = QPushButton()
        self.start_button.setText("Start animation")
        self.start_button.clicked.connect(self.start_cats_animation)
        self.start_button.pressed.connect(self.start_cats_animation)

        # Initially, no dots widget is created
        self.dots = None

        # Add input fields and button to the layout
        self.left_side.addWidget(self.input_number)
        self.left_side.addWidget(self.input_radius)
        self.left_side.addWidget(self.start_button)

        # Add left interactive part to the main layout
        self.layout.addLayout(self.left_side)

        # Create a central widget and set the layout
        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

    def set_cats_number(self, n):
        self.cats_number = int(n)

    def set_radius(self, r):
        self.radius = int(r)

    def start_cats_animation(self):
        # Get the number and radius from the QLineEdit
        self.cats_number = int(self.input_number.text())
        self.radius = int(self.input_radius.text())
        n = self.input_number.text()

        if n.isdigit():  # Ensure the input is a valid number
            n = int(n)

            # If there is already a dots widget, remove it
            if self.dots is not None:
                self.layout.removeWidget(self.dots)
                self.dots.deleteLater()  # Properly delete the old widget

            # Create a new instance of DrawCats with the specified number of dots
            generator = CatGenerator(
                self.cats_number, self.radius, self.width, self.height
            )
            self.dots = DrawCats(n, generator)
            self.layout.addWidget(self.dots)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
