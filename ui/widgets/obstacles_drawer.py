from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QWidget


class ObstaclesDrawer(QWidget):
    def __init__(self, height, width):
        super().__init__()

        self.label = QLabel(self)
        self.setMinimumSize(1500, 1000)
        self.canvas = QtGui.QPixmap(width, height)
        self.canvas.fill(Qt.white)
        self.label.setPixmap(self.canvas)
        self.start_x, self.start_y = None, None
        self.end_x, self.end_y = None, None
        self.drawing = False
        self.lines = []

    def mousePressEvent(self, e):
        self.start_x, self.start_y = e.x(), e.y()
        self.drawing = True

    def mouseMoveEvent(self, e):
        if self.drawing:
            self.end_x, self.end_y = e.x(), e.y()
            self.update()  # Trigger paintEvent to redraw the line in real-time

    def mouseReleaseEvent(self, e):
        if self.drawing:
            self.end_x, self.end_y = e.x(), e.y()
            self.finalize_line()
            self.drawing = False

    def finalize_line(self):
        self.lines.append(((self.start_x, self.start_y), (self.end_x, self.end_y)))
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self.label.pixmap())
        painter.fillRect(self.rect(), Qt.white)  # Clear canvas with white
        painter.end()

        painter.begin(self.label.pixmap())
        pen = QtGui.QPen()
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
