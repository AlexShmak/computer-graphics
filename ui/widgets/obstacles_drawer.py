import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel


class ObstaclesDrawer(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the canvas
        self.label = QLabel()
        self.canvas = QtGui.QPixmap(600, 600)
        self.canvas.fill(Qt.white)  # Set initial canvas color to white
        self.label.setPixmap(self.canvas)

        # Variables to store the current and last mouse positions
        self.start_x, self.start_y = None, None
        self.end_x, self.end_y = None, None
        self.drawing = False  # Flag to track if we are currently drawing
        self.lines = []  # List to store all the finalized lines

    def mousePressEvent(self, e):
        # Start drawing: store the starting point
        self.start_x, self.start_y = e.x(), e.y()
        self.drawing = True

    def mouseMoveEvent(self, e):
        # Update the end point while drawing
        if self.drawing:
            self.end_x, self.end_y = e.x(), e.y()
            self.update()  # Trigger paintEvent to redraw the line in real-time

    def mouseReleaseEvent(self, e):
        # Store the final endpoint and stop drawing
        if self.drawing:
            self.end_x, self.end_y = e.x(), e.y()
            self.finalize_line()  # Store the final line
            self.drawing = False  # Reset drawing flag

    def finalize_line(self):
        # Store the current line in the lines list
        self.lines.append(((self.start_x, self.start_y), (self.end_x, self.end_y)))
        self.update()  # Trigger repaint after finalizing the line

    def paintEvent(self, event):
        # Clear the canvas by filling it with white color
        painter = QtGui.QPainter(self.label.pixmap())
        painter.fillRect(self.rect(), Qt.white)  # Clear canvas with white
        painter.end()

        # Redraw all the finalized lines
        painter.begin(self.label.pixmap())
        pen = QtGui.QPen()  # QtGui.QColor("green"))
        pen.setWidth(2)
        painter.setPen(pen)

        # Draw the previously finalized lines
        for line in self.lines:
            (x1, y1), (x2, y2) = line
            painter.drawLine(x1, y1, x2, y2)

        # Draw the current line while dragging
        if (
            self.start_x is not None
            and self.start_y is not None
            and self.end_x is not None
            and self.end_y is not None
        ):
            painter.drawLine(self.start_x, self.start_y, self.end_x, self.end_y)

        painter.end()
