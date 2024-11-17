from PyQt5.QtWidgets import (
    QFrame,
    QWidget,
)


class CatsPanel(QWidget):
    def __init__(self):
        super().__init__()

        # Initially, no cats widget is created
        self.cats = None

        # Create a frame for the cats widget
        self.cats_frame = QFrame(self)
        self.cats_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.cats_frame.setFrameShadow(QFrame.Shadow.Raised)

        # Create a layout for the cats frame
        self.cats_layout = None
