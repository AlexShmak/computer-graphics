import os
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# ? needed when importing `generator`
sys.path.append(os.getcwd())

from generator.generator import CatGenerator
from widgets import input_panel, cats_drawer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.generator = None
        self.cats_number = None
        self.radius = None
        self.r0 = None
        self.r1 = None

        self.layout = QHBoxLayout()

        # Set the main window and get its geometry
        self.setWindowTitle("Cats")
        self.setMinimumSize(1000, 1000)

        self.input_panel = input_panel.InputPanel()

        # Set the button to start animation
        self.start_button = QPushButton("Start animation")
        self.start_button.clicked.connect(self.start_cats_animation)

        self.input_panel.input_layout.addWidget(self.start_button)

        # Add the left frame to the main layout
        self.layout.addWidget(self.input_panel.input_frame)

        # Create a frame for the dots widget
        self.dots_frame = QFrame(self)
        self.dots_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.dots_frame.setFrameShadow(QFrame.Shadow.Raised)

        # Create a layout for the dots frame
        self.dots_layout = None

        # Add the dots frame to the main layout
        self.layout.addWidget(self.dots_frame)

        # Set the main layout to the central widget
        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        # Initially, no dots widget is created
        self.dots = None

    def start_cats_animation(self):
        if self.dots is None:
            self.dots_layout = QVBoxLayout(self.dots_frame)

        # Get the number and radius from the QLineEdit
        self.cats_number = self.input_panel.number.text().strip()
        self.radius = self.input_panel.radius.text().strip()
        self.r0 = self.input_panel.r0.text().strip()
        self.r1 = self.input_panel.r1.text().strip()

        if (
            self.cats_number.isdigit() and self.radius.isdigit()
        ):  # Ensure inputs are valid numbers
            self.cats_number = int(self.cats_number)
            self.radius = int(self.radius)

            # If there is already a dots widget, remove it
            if self.dots is not None:
                self.dots_layout.removeWidget(self.dots)
                self.dots.deleteLater()  # Properly delete the old widget

            # Ensure the dots frame is resized to fit the dots widget
            self.input_panel.input_frame.setMaximumSize(300, 2000)
            self.dots_frame.setMinimumSize(
                700, 400
            )  # Set a minimum size for the dots frame
            # Create a new instance of DrawCats with the specified number of dots
            generator = CatGenerator(
                self.cats_number,
                self.radius,
                self.dots_frame.width(),
                self.dots_frame.height(),
            )
            self.dots = cats_drawer.CatsDrawer(self.cats_number, generator)
            self.dots_layout.addWidget(
                self.dots
            )  # Add the new dots widget to the dots layout

            # Update the layout to reflect changes
            self.dots_frame.setLayout(
                self.dots_layout
            )  # Set the layout of the dots frame


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


"""
FIXME: fix resizing window

TODO:

* get statuses from algorithm
    * * Add sleepy cats
    * * Add hit cats
    * * Add eating cats
* Add control for smoothness based on the number of cats (probably slider)
* Separate widgets from MainWindow 

DONE:

* Draw frames for widgets 
* Add signs for number and radius input fields
* Add fields to set r0 and r1 manually (to calculate cats' states)

"""
