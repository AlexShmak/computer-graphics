import pygame
import numpy as np
from ui.resources import catstate_to_color, catstate_to_picture, FoodState

DOT_SIZE = 1
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
    coords1,
    coords2,
    current_coords,
    states,
    window_surface,
    obstacles,
    food,
    draw_method,
):
    x1, y1 = coords1
    x2, y2 = coords2
    cx, cy = current_coords

    # Determine whether to draw interpolated or final positions
    delta_x = np.abs(x2 - x1) >= RES[0] // 2
    delta_y = np.abs(y2 - y1) >= RES[1] // 2

    draw_final = np.logical_or(delta_x, delta_y)

    x_draw = np.where(draw_final, x2, np.array(cx, dtype=int))
    y_draw = np.where(draw_final, y2, np.array(cy, dtype=int))

    for x, y, state in zip(x_draw, y_draw, states):
        draw_method(window_surface, int(x), int(y), state)

        # Draw obstacles (lines)
    for start, end in obstacles:
        pygame.draw.line(window_surface, (255, 0, 0), start, end, 2)

    for i in range(food.shape[1]):
        draw_method(window_surface, int(food[0][i]), int(food[1][i]), FoodState.FOOD)
