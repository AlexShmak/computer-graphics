from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QWidget


class ObstaclesDrawer(QWidget):
    """
    A widget for drawing obstacles on a canvas.
    """

    def __init__(self, height, width):
        """
        Initializes the ObstaclesDrawer widget.

        Parameters
        ----------
        height : int
            The height of the drawing canvas.
        width : int
            The width of the drawing canvas.

        Notes
        -----
        This constructor sets up the QLabel with a white QPixmap of specified dimensions
        to act as the canvas for drawing. Initializes the drawing state and line storage.
        """
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
        """
        Initiates the drawing process on mouse press.

        Parameters
        ----------
        e : QMouseEvent
            The mouse event containing information about the mouse press, including
            the position of the cursor.

        Notes
        -----
        Sets the starting coordinates for drawing and marks the drawing state as active.
        """
        self.start_x, self.start_y = e.x(), e.y()
        self.drawing = True

    def mouseMoveEvent(self, e):
        """
        Updates the end coordinates of the line while the mouse is being dragged.

        Parameters
        ----------
        e : QMouseEvent
            The mouse event containing information about the mouse position.

        Notes
        -----
        Updates the end coordinates for drawing and triggers a repaint event to
        redraw the line in real-time.
        """
        if self.drawing:
            self.end_x, self.end_y = e.x(), e.y()
            self.update()  # Trigger paintEvent to redraw the line in real-time

    def mouseReleaseEvent(self, e):
        """
        Finalizes the drawing of a line on mouse release.

        Parameters
        ----------
        e : QMouseEvent
            The mouse event containing information about the mouse release, including
            the position of the cursor.

        Notes
        -----
        Updates the end coordinates for drawing, finalizes the line by adding it to the lines
        list, and marks the drawing state as inactive.
        """
        if self.drawing:
            self.end_x, self.end_y = e.x(), e.y()
            self.finalize_line()
            self.drawing = False

    def finalize_line(self):
        """
        Finalizes the current line being drawn.

        Notes
        -----
        Adds the current line's start and end coordinates to the list of lines,
        and updates the widget to trigger a repaint.
        """
        self.lines.append(((self.start_x, self.start_y), (self.end_x, self.end_y)))
        self.update()

    def paintEvent(self, event):
        """
        Handles the paint event for the ObstaclesDrawer widget by redrawing the previously finalized lines and
        the current line being drawn.

        Parameters
        ----------
        event : QPaintEvent
            The paint event containing information about the region that needs to be redrawn.

        Notes
        -----
        This function clears the canvas with white, redraws the previously finalized lines, and draws the current line
        while dragging. It is triggered by the update() method.
        """

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
