from PyQt5.QtWidgets import (
    QFrame,
    QWidget,
)


class ObstaclesPanel(QWidget):
    """
    A class representing a panel for displaying obstacles-related widgets.
    """

    def __init__(self):
        """
        Initializes the ObstaclesPanel widget.

        This constructor sets up the initial structure of the ObstaclesPanel,
        including creating a frame for displaying obstacles-related widgets
        and initializing layout attributes for organizing the frame contents.
        Initially, no obstacles widget is associated with the panel.
        """
        super().__init__()

        # Initially, no cats widget is created
        self.obstacles_drawer = None

        # Create a frame for the cats widget
        self.obst_frame = QFrame(self)
        self.obst_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.obst_frame.setFrameShadow(QFrame.Shadow.Raised)

        # Create a layout for the cats frame
        self.obst_layout = None
