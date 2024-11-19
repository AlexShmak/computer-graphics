import os
import sys
import time

import numpy as np
from PyQt5.QtCore import QPoint, Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QWidget

sys.path.append(os.getcwd())

from algoritm.common import EAT, FIGHT, HISS, HIT, SLEEP, WALK
from algoritm.states_update import update_states
from generator.generator import CatGenerator


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

        self.scale_factor = 0.4  # Initial scale factor (1.0 means 100%)
        self.offset = QPoint(0, 0)  # Offset for dragging the scene

        # Resize images once based on scale_factor
        self.resize_images()

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

        # Draw bad borders (scaled)
        if self.bad_borders:
            for bad_border in self.bad_borders:
                start_point = self.convert_to_qpoint(bad_border[0])
                end_point = self.convert_to_qpoint(bad_border[1])

                # Scale the points and draw the line
                scaled_start = self.scale_point(start_point)
                scaled_end = self.scale_point(end_point)
                painter.drawLine(scaled_start, scaled_end)

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
                + (self.coordinates[0][i] - self.prev_coordinates[0][i]) * move_factor
            )
            y = int(
                self.prev_coordinates[1][i]
                + (self.coordinates[1][i] - self.prev_coordinates[1][i]) * move_factor
            )
            image_position = QPoint(x, y)

            # Apply offset and scaling
            image_position = self.scale_point(image_position)

            # Draw the cat based on its state
            if state in self.images:
                pixmap = self.images[state]
                image_position = QPoint(
                    image_position.x()
                    - pixmap.width() // 2,  # Subtract half of the width to center
                    image_position.y()
                    - pixmap.height() // 2,  # Subtract half of the height to center
                )
                painter.drawPixmap(image_position, pixmap)

        # Draw food (scaled)
        for j in range(self.food_num):
            x = int(self.generator.food[0][j])
            y = int(self.generator.food[1][j])
            image_position = QPoint(x, y)

            # Apply offset and scaling
            image_position = self.scale_point(image_position)

            # Adjust position to center the food
            image_position = QPoint(
                image_position.x() - self.images["food"].width() // 2,
                image_position.y() - self.images["food"].height() // 2,
            )

            painter.drawPixmap(image_position, self.images["food"])

        # Get the widget's size
        widget_size = self.size()  # Size of the widget (width, height)

        # Create the top-left and bottom-right points of the bounding box
        top_left = QPoint(0, 0)
        bottom_right = QPoint(widget_size.width(), widget_size.height())

        # Now, scale the bounding box (top-left and bottom-right) using the scale factor and offset
        scaled_top_left = self.scale_point(top_left)
        scaled_bottom_right = self.scale_point(bottom_right)

        # Set the border color and width for the bounding box
        painter.setPen(QPen(QColor("black"), 2, Qt.SolidLine))
        painter.setBrush(Qt.NoBrush)

        # Draw the rectangle (bounding box) around the whole widget
        painter.drawRect(
            scaled_top_left.x(),
            scaled_top_left.y(),
            scaled_bottom_right.x() - scaled_top_left.x(),
            scaled_bottom_right.y() - scaled_top_left.y(),
        )

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

    def scale_point(self, point: QPoint) -> QPoint:
        """Scales the given point by the current zoom level (scale_factor) and applies the offset for drag."""
        # Take the scale factor into account while adjusting the point for drag
        return QPoint(
            int((point.x() - self.offset.x()) * self.scale_factor),
            int((point.y() - self.offset.y()) * self.scale_factor),
        )

    def resize_images(self):
        """Resizes all images based on the current scale factor with high-quality interpolation."""
        for key, image in self.images.items():
            # For example, only resize if the scale factor is large enough
            if self.scale_factor <= 1.0:
                scale = 1.0
            elif self.scale_factor <= 1.5:
                scale = 1.5
            elif self.scale_factor <= 2.0:
                scale = 2.0
            else:
                scale = 2.5  # cap at 2.5x for example

            # Cache or use a pre-scaling strategy
            self.images[key] = image.scaled(
                int(scale * 100),
                int(scale * 100),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

    def wheelEvent(self, event):
        """Handles zooming in and out with the mouse wheel."""
        zoom_factor = 1.1
        if event.angleDelta().y() < 0:  # Scroll down (zoom out)
            self.scale_factor /= zoom_factor
        else:  # Scroll up (zoom in)
            self.scale_factor *= zoom_factor

        # Resize the images according to the new scale factor
        self.resize_images()

        # Repaint the widget after zooming
        self.update()

    def mousePressEvent(self, event):
        """Handles mouse press for drag functionality."""
        if event.button() == Qt.LeftButton:
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        """Handles mouse movement for drag functionality."""
        if event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.last_pos
            self.offset -= delta
            self.last_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """Handles mouse release after dragging."""
        if event.button() == Qt.LeftButton:
            self.last_pos = None

    def convert_to_qpoint(self, point):
        """Converts a tuple to QPoint if it's not already a QPoint."""
        if isinstance(point, tuple):
            return QPoint(point[0], point[1])
        return point
