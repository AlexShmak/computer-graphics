import os
import sys

from PyQt5.QtCore import QPoint, QTimer
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import (
    QWidget,
)

sys.path.append(os.getcwd())
from generator.generator import CatGenerator


class CatsDrawer(QWidget):
    def __init__(self, n, generator: CatGenerator):
        super().__init__()
        self.cats_num = n

        self.generator = generator
        self.coordinates = generator.cats
        self.prev_coordinates = generator.cats

        # Set up a timer to update positions
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_positions)
        self.timer.start(100)

    def paintEvent(self, event):
        # Create a QPainter object to perform the drawing
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(3)
        painter.setPen(pen)

        # for i in range(self.cats_num):
        #     painter.drawPoint(
        #         QPoint(int(self.coordinates[0][i]), int(self.coordinates[1][i]))
        #     )

        # * Smoother animation
        # FIXME: make dependant on the number of cats
        for factor in range(1, 10):
            for i in range(self.cats_num):
                x = int(
                    self.prev_coordinates[0][i]
                    + (self.coordinates[0][i] - self.prev_coordinates[0][i])
                    * factor
                    * 0.1
                )
                y = int(
                    self.prev_coordinates[1][i]
                    + (self.coordinates[1][i] - self.prev_coordinates[1][i])
                    * factor
                    * 0.1
                )

                painter.drawPoint(QPoint(x, y))

    def update_positions(self):
        self.prev_coordinates = self.coordinates
        self.generator.update_cats()
        self.coordinates = self.generator.cats

        self.update()  # Trigger another iteration of painting
