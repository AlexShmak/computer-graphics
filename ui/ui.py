"""Graphical User Interface (GUI) Module for Cats App"""

import os
import sys
import time

import pygame
import pygame_gui
import numpy as np

sys.path.append(os.getcwd())

from algorithm.algorithm import CatAlgorithm
from generator.generator import CatGenerator
from processor.processor import CatProcessor


INTER_FRAME_NUM = 60  # Number of interpolated frames
DOT_SIZE = 1
RES = (1500, 1000)
FPS = 60


# Precompute state-to-color mappings
STATE_COLORS = {
    1: (65, 105, 225),  # walk
    2: (255, 140, 0),  # hiss
    3: (255, 0, 0),  # fight
    4: (0, 255, 127),  # eat
    5: (128, 128, 128),  # hit
    6: (106, 255, 255),  # sleep
}


def index_to_color(ind: int):
    """Map state index to a color."""
    return STATE_COLORS.get(ind, (255, 255, 255))  # Default to white


def draw_dots(coords1, coords2, current_coords, states, window_surface, obstacles):
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
        pygame.draw.circle(
            window_surface,
            index_to_color(state),
            (x_draw, y_draw),
            DOT_SIZE,
        )


def run_ui():
    """Function to run Pygame GUI"""

    pygame.init()

    pygame.display.set_caption("Cats")
    window_surface = pygame.display.set_mode(RES)
    background_surface = pygame.Surface(RES)
    background_surface.fill((0, 0, 0))

    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager(RES)

    # UI Initialization
    def create_label(text, pos):
        return pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(pos, (300, 25)),
            text=text,
            manager=manager,
        )

    def create_input(pos):
        return pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(pos, (300, 30)), manager=manager
        )

    def create_button(text, pos):
        return pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(pos, (300, 50)),
            text=text,
            manager=manager,
        )

    labels = [
        create_label("Number of cats", (50, 25)),
        create_label("Maximum travel distance", (50, 85)),
        create_label("Cats start hissing at a distance", (50, 145)),
        create_label("Cats start fighting at a distance", (50, 205)),
    ]

    input_fields = [
        create_input((50, 50)),
        create_input((50, 110)),
        create_input((50, 170)),
        create_input((50, 230)),
    ]

    buttons = {
        "draw_obstacles": create_button("Draw obstacles", (50, 280)),
        "start": create_button("Start animation", (50, 340)),
        "pause": create_button("Pause/Resume", (50, 400)),
        "quit": create_button("Quit", (50, 460)),
    }

    # State Variables
    is_running = False
    is_paused = False
    current_frame = 0

    generator = CatGenerator(0, 0, *RES)
    algo = CatAlgorithm(*RES, 0, 5, 10, 1000)
    processor = CatProcessor(algo, generator)

    coords1, states1, coords2, states2 = None, None, None, None
    delta_dist = None

    # Obstacle variables
    obstacles = []
    drawing_obstacles = False
    start_pos = None

    def initialize_processor(n, r, r0, r1):
        nonlocal generator, processor, coords1, states1, coords2, states2, delta_dist
        generator = CatGenerator(n, r, *RES)
        for obstacle in obstacles:
            generator.add_bad_border(obstacle[0], obstacle[1])
            print(obstacle)
        algo = CatAlgorithm(*RES, n, r0, r1)
        processor = CatProcessor(algo, generator)
        processor.start()

        coords1, states1 = processor.data.unpack()
        coords2, states2 = processor.data.unpack()
        delta_dist = (coords2 - coords1) / INTER_FRAME_NUM

    # Main Loop
    while True:
        time_delta = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                processor.stop()
                sys.exit()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == buttons["quit"]:
                    pygame.quit()
                    processor.stop()
                    sys.exit()

                if event.ui_element == buttons["start"]:
                    print(obstacles)
                    try:
                        n, r, r1, r0 = (int(field.get_text()) for field in input_fields)
                        if is_running:
                            processor.stop()
                        initialize_processor(n, r, r0, r1)
                        is_running = True
                        is_paused = False
                        current_frame = 0
                    except ValueError:
                        pass

                if event.ui_element == buttons["pause"] and is_running:
                    is_paused = not is_paused

                # Disable "Draw obstacles" button when animation is running
                if event.ui_element == buttons["draw_obstacles"] and not is_running:
                    drawing_obstacles = not drawing_obstacles

            manager.process_events(event)

            # Handle mouse events for drawing obstacles
            if drawing_obstacles and not is_running:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    start_pos = event.pos
                elif event.type == pygame.MOUSEMOTION:
                    if start_pos:
                        # Clear the screen to ensure the background is visible
                        window_surface.blit(background_surface, (0, 0))

                        # Draw the line dynamically as the mouse moves
                        pygame.draw.line(
                            window_surface, (255, 200, 200), start_pos, event.pos, 2
                        )

                        # Draw existing obstacles
                        for start, end in obstacles:
                            pygame.draw.line(
                                window_surface, (255, 200, 200), start, end, 2
                            )

                elif event.type == pygame.MOUSEBUTTONUP:
                    if start_pos:
                        end_pos = event.pos
                        obstacles.append((start_pos, end_pos))  # Save the line
                        start_pos = None  # Reset the start position after drawing

        if not drawing_obstacles:
            window_surface.blit(background_surface, (0, 0))  # Redraw the background

        if is_running and not is_paused:
            if current_frame < INTER_FRAME_NUM:
                current_coords = coords1 + delta_dist * current_frame
            else:
                current_coords = coords2

            draw_dots(
                coords1, coords2, current_coords, states1, window_surface, obstacles
            )

            current_frame = (current_frame + 1) % INTER_FRAME_NUM
            if current_frame == 0:
                coords1, states1 = coords2, states2
                coords2, states2 = processor.data.unpack()
                delta_dist = (coords2 - coords1) / INTER_FRAME_NUM
        else:
            if coords1 is not None:
                draw_dots(
                    coords1, coords2, current_coords, states1, window_surface, obstacles
                )

        # Redraw all obstacles after updating the window
        for start, end in obstacles:
            pygame.draw.line(window_surface, (255, 0, 0), start, end, 2)

        pygame.display.set_caption(f"Cats  |  {clock.get_fps():.2f}")
        manager.update(time_delta)
        manager.draw_ui(window_surface)
        pygame.display.update()
