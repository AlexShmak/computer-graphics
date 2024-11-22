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
from widgets import (
    cats_drawer,
    cats_panel,
    input_panel,
    obstacles_drawer,
    obstacles_panel,
)

sys.path.append(os.getcwd())


from generator.generator import CatGenerator


class MainWindow(QMainWindow):
    """
    Main window for the application. Contains the input panel, cats panel, and obstacles panel.
    """

    def __init__(self):
        """
        Constructor for the main window.

        Sets up the window with a horizontal layout that contains the input panel,
        the cats panel, and the obstacles panel.
        The input panel contains fields to input the number of cats, the radius of the cats,
        and the r0 and r1 values.
        The cats panel contains a frame to display the cats.
        The obstacles panel contains a frame to draw obstacles.
        The window also contains buttons to start the animation, draw obstacles,
        and pause/resume the animation.

        :return: None
        """
        super().__init__()

        self.generator = None
        self.cats_number = None
        self.radius = None
        self.r0 = None
        self.r1 = None

        self.lines = []

        self.layout = QHBoxLayout()

        # Set the main window and get its geometry
        self.setWindowTitle("Cats")
        self.setMinimumSize(1500, 1000)

        self.input_panel = input_panel.InputPanel()
        self.cats_panel = cats_panel.CatsPanel()
        self.obst_panel = obstacles_panel.ObstaclesPanel()

        self.is_paused = False

        # Set the button to draw obstacles
        self.draw_obstacles_button = QPushButton("Draw Obstacles")
        self.draw_obstacles_button.clicked.connect(self.draw_obstacles)

        # Set the button to start animation
        self.start_button = QPushButton("Start animation")
        self.start_button.clicked.connect(self.start_cats_animation)

        # Set the pause/resume button
        self.pause_button = QPushButton("Pause animation", self)
        self.pause_button.clicked.connect(self.toggle_pause)

        self.input_panel.input_layout.addWidget(self.draw_obstacles_button)
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
        """
        Starts the animation of the cats.

        Gets the number of cats, radius, r0, and r1 from the QLineEdit and creates a new instance of CatGenerator with the specified number of cats.
        If there is already a cats widget, removes it and replaces it with a new one.
        Ensures the cats frame is resized to fit the cats widget.

        :return: None
        """
        self.cats_number = self.input_panel.number.text().strip()
        self.radius = self.input_panel.radius.text().strip()
        self.r0 = self.input_panel.r0.text().strip()
        self.r1 = self.input_panel.r1.text().strip()
        self.pause_button.setText("Pause animation")
        self.is_paused = False

        if (
            self.cats_number.isdigit()
            and self.radius.isdigit()
            and self.r0.isdigit()
            and self.r1.isdigit()
        ):  # Ensure inputs are valid numbers
            if self.obst_panel.obstacles_drawer is not None:
                self.obst_panel.obst_frame.hide()
                self.cats_panel.cats_frame.show()
                self.lines = self.obst_panel.obstacles_drawer.lines

            __cats_panel = self.cats_panel

            if __cats_panel.cats_drawer is None:
                __cats_panel.cats_layout = QVBoxLayout(__cats_panel.cats_frame)

            self.cats_number = int(self.cats_number)
            self.radius = int(self.radius)
            self.r0 = int(self.r0) * 50
            self.r1 = int(self.r1) * 50

            # If there is already a cats widget, remove it
            if __cats_panel.cats_drawer is not None:
                __cats_panel.cats_layout.removeWidget(__cats_panel.cats_drawer)
                __cats_panel.cats_drawer.deleteLater()  # Properly delete the old widget

            # Ensure the cats frame is resized to fit the cats widget
            self.input_panel.input_frame.setMaximumSize(300, self.height())
            __cats_panel.cats_frame.setMinimumSize(
                1000, 500
            )  # Set a minimum size for the cats frame

            # Create a new instance of CatGenerator with the specified number of cats
            generator = CatGenerator(
                self.cats_number,
                self.radius,
                __cats_panel.cats_frame.width(),
                __cats_panel.cats_frame.height(),
            )
            __cats_panel.cats_drawer = cats_drawer.CatsDrawer(
                self.cats_number, generator, self.r0, self.r1, self.lines
            )
            __cats_panel.cats_layout.addWidget(
                __cats_panel.cats_drawer
            )  # Add the new cats widget to the cats layout

            # Update the layout to reflect changes
            __cats_panel.cats_frame.setLayout(
                __cats_panel.cats_layout
            )  # Set the layout of the cats frame

    def toggle_pause(self):
        """
        Toggles the pause state of the animation.

        This function pauses or resumes the animation for the cats and hides
        or shows the obstacles frame accordingly. It also updates the text
        on the pause button to indicate the current state (either "Pause Animation"
        or "Resume Animation").

        If the obstacles drawer is active, it hides the obstacles frame.
        If the cats drawer is active, it toggles the paused state of the cats animation.
        """
        if (
            self.cats_panel.cats_drawer is not None
            or self.obst_panel.obstacles_drawer is not None
        ):
            if self.obst_panel.obstacles_drawer is not None:
                self.obst_panel.obst_frame.hide()
            self.is_paused = not self.is_paused
            if self.cats_panel.cats_drawer is not None:
                self.cats_panel.cats_drawer.is_paused = (
                    not self.cats_panel.cats_drawer.is_paused
                )
            if self.is_paused:
                self.pause_button.setText("Resume Animation")
                self.obst_panel.obst_frame.hide()
                self.cats_panel.cats_frame.show()
            else:
                self.pause_button.setText("Pause Animation")

    def draw_obstacles(self):
        # Remove the cats frame if it exists, as we're switching to obstacles drawing
        """
        Starts the obstacles drawing mode.

        This function hides the cats frame and shows the obstacles frame. It
        then adds the obstacles frame to the layout and initializes the
        obstacles layout if it hasn't been initialized. If there is already an
        obstacles widget, it removes the old widget and creates a new instance
        of ObstaclesDrawer for the user to draw obstacles. Finally, it updates
        the layout to reflect changes.
        """
        if self.cats_panel.cats_frame is not None:
            self.cats_panel.cats_frame.hide()
            self.obst_panel.obst_frame.show()

        # Add the obstacles frame to the layout
        self.layout.addWidget(self.obst_panel.obst_frame)

        __obst_panel = self.obst_panel

        if __obst_panel.obstacles_drawer is None:
            # Initialize the obstacles layout if it hasn't been initialized
            __obst_panel.obst_layout = QVBoxLayout(__obst_panel.obst_frame)

        # If there is already an obstacles widget, remove it
        if __obst_panel.obstacles_drawer is not None:
            __obst_panel.obst_layout.removeWidget(__obst_panel.obstacles_drawer)
            __obst_panel.obstacles_drawer.deleteLater()  # Properly delete the old widget

        # Ensure the obstacles frame is resized to fit the obstacles widget
        self.input_panel.input_frame.setMaximumSize(300, self.height())
        __obst_panel.obst_frame.setMaximumSize(self.width(), self.height())

        # Create a new instance of ObstaclesDrawer for the user to draw obstacles
        __obst_panel.obstacles_drawer = obstacles_drawer.ObstaclesDrawer(
            # __obst_panel.obst_frame.height(), __obst_panel.obst_frame.width()
            self.height(),
            self.width(),
        )
        __obst_panel.obst_layout.addWidget(__obst_panel.obstacles_drawer)

        # Update the layout to reflect changes
        __obst_panel.obst_frame.setLayout(__obst_panel.obst_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
