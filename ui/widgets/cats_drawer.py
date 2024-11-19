import time
from generator.generator import CatGenerator
from algoritm.states_update import update_states
from algoritm.common import EAT, FIGHT, HISS, HIT, SLEEP, WALK
import os
import sys

import numpy as np
from PyQt5.QtCore import QPoint, Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QWidget

sys.path.append(os.getcwd())


def update_extra_states(sleepy_ids, hit_ids, eating_ids, states):
    for i in sleepy_ids:
        states[i] = SLEEP
    for j in hit_ids:
        states[j] = HIT
    for k in eating_ids:
        states[int(k)] = EAT


class CatsDrawer(QWidget):
    def __init__(self, n, generator: CatGenerator, r0: int, r1: int, lines: list):
        super().__init__()

        self.is_paused = False
        self.cats_num = n
        self.states = np.full(self.cats_num, WALK, dtype=np.uint8)

        # Load images
        self.images = {
            SLEEP: QPixmap("images/sleep.png"),
            EAT: QPixmap("images/eat.png"),
            HISS: QPixmap("images/hiss.png"),
            FIGHT: QPixmap("images/fight.png"),
            HIT: QPixmap("images/hit.png"),
            WALK: QPixmap("images/walk.png"),
            "food": QPixmap("images/food.png"),
        }

        self.scale_factor = 40

        # Resize images once
        for key, image in self.images.items():
            self.images[key] = image.scaled(
                self.scale_factor, self.scale_factor, Qt.KeepAspectRatio
            )

        self.generator = generator
        self.coordinates = self.generator.cats
        self.prev_coordinates = self.generator.cats

        self.bad_borders = lines

        if self.bad_borders:
            for line in self.bad_borders:
                self.generator.add_bad_border(line[0], line[1])

        update_states(self.coordinates, r0, r1, self.states)

        self.sleepy_cat_ids = self.generator.sleepy_cat_ids
        self.hit_cat_ids = self.generator.hit_cat_ids
        self.eating_cat_ids = self.generator.eating_cat_ids

        update_extra_states(
            self.sleepy_cat_ids, self.hit_cat_ids, self.eating_cat_ids, self.states
        )
        self.food_num = len(self.generator.food[0])

        # Time-based animation settings
        self.last_time = time.time()
        self.animation_speed = 0.1  # Control how fast the cats move in the animation

        # Set up a timer to update positions
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.update_positions(r0, r1))
        self.timer.start(30)  # Update every 30ms

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(10)
        pen.setColor(QColor("brown"))
        painter.setPen(pen)

        # Draw bad borders
        if self.bad_borders:
            for bad_border in self.bad_borders:
                painter.drawLine(*bad_border[0], *bad_border[1])

        # Calculate how much time has passed to adjust interpolation
        current_time = time.time()
        elapsed_time = current_time - self.last_time
        self.last_time = current_time

        # Adjust the speed of movement based on elapsed time (for frame rate independence)
        move_factor = elapsed_time / self.animation_speed

        # Smoother animation by drawing cats in intermediate positions
        for i in range(self.cats_num):
            state = self.states[i]
            # Calculate new position for smooth transition
            x = int(
                self.prev_coordinates[0][i]
                + (self.coordinates[0][i] -
                   self.prev_coordinates[0][i]) * move_factor
            )
            y = int(
                self.prev_coordinates[1][i]
                + (self.coordinates[1][i] -
                   self.prev_coordinates[1][i]) * move_factor
            )
            image_position = QPoint(x, y)

            # Draw the cat based on its state
            if state in self.images:
                painter.drawPixmap(image_position, self.images[state])

        # Draw food
        for j in range(self.food_num):
            image_position = QPoint(
                int(self.generator.food[0][j]), int(self.generator.food[1][j])
            )
            painter.drawPixmap(image_position, self.images["food"])

        self.update()

    def update_positions(self, r0, r1):
        if not self.is_paused:
            # Ensure coordinates are updated
            self.prev_coordinates = self.coordinates
            self.generator.update_cats()

            self.coordinates = self.generator.cats

            self.sleepy_cat_ids = self.generator.sleepy_cat_ids
            self.hit_cat_ids = self.generator.hit_cat_ids
            self.eating_cat_ids = self.generator.eating_cat_ids

            update_states(self.coordinates, r0, r1, self.states)
            update_extra_states(
                self.sleepy_cat_ids, self.hit_cat_ids, self.eating_cat_ids, self.states
            )

            # Trigger a repaint of the entire widget
            self.update()
