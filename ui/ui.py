import os
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# ? needed when importing `generator`
sys.path.append(os.getcwd())

from generator.generator import CatGenerator
from widgets import input_panel, cats_panel, cats_drawer


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
        self.cats_panel = cats_panel.CatsPanel()

        # Set the button to start animation
        self.start_button = QPushButton("Start animation")
        self.start_button.clicked.connect(self.start_cats_animation)

        self.is_paused = False

        # Set the pause/resume button
        self.pause_button = QPushButton("Pause animation", self)
        self.pause_button.clicked.connect(self.toggle_pause)

        self.input_panel.input_layout.addWidget(self.start_button)
        self.input_panel.input_layout.addWidget(self.pause_button)

        # Add the left frame to the main layout
        self.layout.addWidget(self.input_panel.input_frame)

        # Add the cats frame to the main layout
        self.layout.addWidget(self.cats_panel.cats_frame)

        # Set the main layout to the central widget
        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

    def start_cats_animation(self):
        __panel = self.cats_panel

        if __panel.cats_drawer is None:
            __panel.cats_layout = QVBoxLayout(__panel.cats_frame)

        # Get the number and radius from the QLineEdit
        self.cats_number = self.input_panel.number.text().strip()
        self.radius = self.input_panel.radius.text().strip()
        self.r0 = self.input_panel.r0.text().strip()
        self.r1 = self.input_panel.r1.text().strip()

        if (
            self.cats_number.isdigit()
            and self.radius.isdigit()
            and self.r0.isdigit()
            and self.r1.isdigit()
        ):  # Ensure inputs are valid numbers
            self.cats_number = int(self.cats_number)
            self.radius = int(self.radius)
            self.r0 = int(self.r0) * 100
            self.r1 = int(self.r1) * 100

            # If there is already a cats widget, remove it
            if __panel.cats_drawer is not None:
                __panel.cats_layout.removeWidget(__panel.cats_drawer)
                __panel.cats_drawer.deleteLater()  # Properly delete the old widget

            # Ensure the cats frame is resized to fit the cats widget
            self.input_panel.input_frame.setMaximumSize(300, 2000)
            __panel.cats_frame.setMinimumSize(
                700, 400
            )  # Set a minimum size for the cats frame
            # Create a new instance of CatsDrawer with the specified number of cats
            generator = CatGenerator(
                self.cats_number,
                self.radius,
                __panel.cats_frame.width(),
                __panel.cats_frame.height(),
            )
            __panel.cats_drawer = cats_drawer.CatsDrawer(
                self.cats_number, generator, self.r0, self.r1
            )
            __panel.cats_layout.addWidget(
                __panel.cats_drawer
            )  # Add the new cats widget to the cats layout

            # Update the layout to reflect changes
            __panel.cats_frame.setLayout(
                __panel.cats_layout
            )  # Set the layout of the cats frame

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.cats_panel.cats_drawer.is_paused = (
            not self.cats_panel.cats_drawer.is_paused
        )
        if self.is_paused:
            self.pause_button.setText("Resume Animation")
        else:
            self.pause_button.setText("Pause Animation")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
