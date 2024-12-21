import pygame
import numpy as np
from ui.resources import catstate_to_color, catstate_to_picture

DOT_SIZE = 10
IMAGE_SCALE = (40, 40)
RES = (1500, 1000)


def draw_dot(window_surface, x_draw, y_draw, state):
    pygame.draw.circle(
        window_surface,
        catstate_to_color(state),
        (x_draw, y_draw),
        DOT_SIZE,
    )


def draw_picture(window_surface, x_draw, y_draw, state):
    window_surface.blit(
        pygame.transform.scale(catstate_to_picture(state), IMAGE_SCALE),
        (x_draw, y_draw),
    )


class DrawStyle:
    DOTS = draw_dot
    PICTURES = draw_picture


def draw_cats(
    coords1, coords2, current_coords, states, window_surface, obstacles, draw_method
):
    x1, y1 = coords1
    x2, y2 = coords2
    cx, cy = current_coords

    # Draw obstacles (lines)
    for start, end in obstacles:
        pygame.draw.line(window_surface, (255, 0, 0), start, end, 2)

    # Determine whether to draw interpolated or final positions
    delta_x = np.abs(x2 - x1) >= RES[0] // 2
    delta_y = np.abs(y2 - y1) >= RES[1] // 2

    for ind, (x, y, state) in enumerate(zip(cx, cy, states)):
        x_draw = x2[ind] if delta_x[ind] or delta_y[ind] else int(x)
        y_draw = y2[ind] if delta_x[ind] or delta_y[ind] else int(y)

        draw_method(window_surface, x_draw, y_draw, state)
