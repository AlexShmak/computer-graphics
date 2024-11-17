import os
import sys

import numpy as np
from PyQt5.QtCore import QPoint, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import (
    QWidget,
)

sys.path.append(os.getcwd())
from algoritm.common import FIGHT, HISS, WALK
from algoritm.states_update import update_states
from generator.generator import CatGenerator


def state2color(state: int) -> str:
    if state == WALK:
        return "green"
    elif state == HISS:
        return "orange"
    else:
        return "red"


class CatsDrawer(QWidget):
    def __init__(self, n, generator: CatGenerator, r0: int, r1: int):
        super().__init__()
        self.cats_num = n
        self.states = np.full(self.cats_num, WALK, dtype=np.uint8)

        self.generator = generator
        self.coordinates = generator.cats
        self.prev_coordinates = generator.cats

        update_states(self.coordinates, r0, r1, self.states)

        # Set up a timer to update positions
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.update_positions(r0, r1))
        self.timer.start(100)

    def paintEvent(self, event):
        # Create a QPainter object to perform the drawing
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(5)
        painter.setPen(pen)

        # for i in range(self.cats_num):
        #     painter.drawPoint(
        #         QPoint(int(self.coordinates[0][i]), int(self.coordinates[1][i]))
        #     )

        # * Smoother animation
        # FIXME: make dependant on the number of cats
        for factor in range(1, 10):
            for i in range(self.cats_num):
                pen.setColor(QColor(state2color(self.states[i])))
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

    def update_positions(self, r0, r1):
        self.prev_coordinates = self.coordinates
        self.generator.update_cats()
        self.coordinates = self.generator.cats
        update_states(self.coordinates, r0, r1, self.states)

        self.update()  # Trigger another iteration of painting
