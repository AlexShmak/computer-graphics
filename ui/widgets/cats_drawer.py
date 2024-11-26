import os
import sys
import time

import numpy as np
from PyQt5.QtCore import QPoint, Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QWidget

sys.path.append(os.getcwd())

from algorithm.common import EAT, FIGHT, HISS, HIT, SLEEP, WALK
from algorithm.states_updater import update_states
from generator.generator import CatGenerator


def update_extra_states(sleepy_ids, hit_ids, eating_ids, states):
    """
    Updates the states of cats that are sleeping, being hit, or eating food.

    Parameters
    ----------
    sleepy_ids : array-like
        The ids of cats that are sleeping.
    hit_ids : array-like
        The ids of cats that are being hit.
    eating_ids : array-like
        The ids of cats that are eating food.
    states : array-like
        The array of states of all cats.

    Notes
    -----
    This function is used to update the states of cats when the generator updates the cats' positions.
    """

    for i in sleepy_ids:
        states[int(i)] = SLEEP
    for j in hit_ids:
        states[int(j)] = HIT
    for k in eating_ids:
        states[int(k)] = EAT


class CatsDrawer(QWidget):
    """
    Widget for drawing cats on a scene.
    """

    def __init__(self, n, generator: CatGenerator, r0: int, r1: int, lines: list):
        """
        Initializes the CatsDrawer widget with the given number of cats and generator.

        Parameters
        ----------
        n : int
            The number of cats to draw.
        generator : CatGenerator
            The generator of the cats.
        r0 : int
            The minimum radius of the cats.
        r1 : int
            The maximum radius of the cats.
        lines : list
            The list of lines that define the bad borders.

        Notes
        -----
        This function initializes the CatsDrawer widget with the given number of cats and generator.
        It loads the images for the states of the cats, sets up the initial positions of the cats, and
        starts a timer to update the positions of the cats every 30ms.
        """
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

        self.scale_factor = 1.0  # Initial scale factor (1.0 means 100%)
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
        """
        Paints the current state of the widget, including cats, bad borders, and food items.

        Parameters
        ----------
        event : QPaintEvent
            The paint event that triggers the drawing process.

        Notes
        -----
        - This method handles the drawing of cats at their interpolated positions between frames
        for smooth animation. The cat images are drawn based on their current states.
        - Bad borders are drawn as lines with a specified pen color and width.
        - Food items are drawn at their respective positions.
        - The entire widget is bounded by a rectangle to depict the widget's size.
        """
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

        # Draw border
        widget_size = self.size()
        top_left = QPoint(0, 0)
        bottom_right = QPoint(widget_size.width(), widget_size.height())
        scaled_top_left = self.scale_point(top_left)
        scaled_bottom_right = self.scale_point(bottom_right)
        painter.setPen(QPen(QColor("black"), 2, Qt.SolidLine))
        painter.setBrush(Qt.NoBrush)

        painter.drawRect(
            scaled_top_left.x(),
            scaled_top_left.y(),
            scaled_bottom_right.x() - scaled_top_left.x(),
            scaled_bottom_right.y() - scaled_top_left.y(),
        )

        self.update()

    def update_positions(self, r0, r1):
        """
        Updates the positions of all cats, and calls the update_states function to update
        the states of the cats based on their new positions.

        Args:
            r0 (int): The radius for FIGHT state.
            r1 (int): The radius for HISS state.

        If the widget is not paused, this function will ensure that the coordinates are
        updated, and then call update_states and update_extra_states to update the states
        of the cats. Finally, it will trigger a repaint of the entire widget.
        """
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
                scale = 0.4
            elif self.scale_factor <= 1.5:
                scale = 0.9
            elif self.scale_factor <= 2.0:
                scale = 1.3
            else:
                scale = 2.0

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
