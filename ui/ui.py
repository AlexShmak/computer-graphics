"""Graphical User Interface (GUI) Module for Cats App"""

import os
import sys
from time import perf_counter

import numpy as np
import pygame
import pygame_gui
import math

sys.path.append(os.getcwd())

from algorithm.algorithm import CatAlgorithm
from generator.generator import CatGenerator
from processor.processor import CatProcessor, CatState
from ui.resources import init_pygame_pictures
from ui.cat_drawer import draw_cats, RES, DrawStyle

INTER_FRAME_NUM = 60  # Number of interpolated frames
TIME_DELTA = 0.001
FPS = 60


def exit_app(processor: CatProcessor):
    pygame.quit()
    if processor:
        processor.stop()
    sys.exit()


def run_ui():
    """Function to run Pygame GUI"""

    pygame.init()

    pygame.display.set_caption("Cats")
    window_surface = pygame.display.set_mode(RES)
    background_surface = pygame.Surface(RES)
    background_surface.fill((0, 0, 0))

    # load cats pictures using pygame
    init_pygame_pictures()

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
        "chage_style": create_button("Change style", (50, 460)),
        "quit": create_button("Quit", (50, 520)),
    }

    # State Variables
    is_running = False
    is_paused = False
    current_frame = 0
    current_style = DrawStyle.PICTURES

    generator: CatGenerator = None
    algorithm: CatAlgorithm = None
    processor: CatProcessor = None

    coords1, states1, coords2, states2, current_coords = None, None, None, None, None
    delta_dist = None

    # Obstacle variables
    obstacles = []
    drawing_obstacles = False
    start_pos = None

    # Frames update
    last_frame_time = 0

    def initialize_processor(n, r, r0, r1):
        nonlocal generator, processor, coords1, states1, coords2, states2, delta_dist
        generator = CatGenerator(n, r, *RES)
        for obstacle in obstacles:
            generator.add_bad_border(obstacle[0], obstacle[1])
            print(obstacle)
        algorithm = CatAlgorithm(*RES, n, r0, r1)
        processor = CatProcessor(algorithm, generator)
        processor.start()

        coords1, states1 = processor.data.unpack()
        coords2, states2 = processor.data.unpack()
        delta_dist = (coords2 - coords1) / INTER_FRAME_NUM

    # Main Loop
    while True:
        time_delta = clock.tick(FPS) / 1000.0
        current_time = perf_counter()
        if current_time - last_frame_time >= TIME_DELTA:
            last_frame_time = current_time  # Update the last frame time
            frame_update = True
        else:
            frame_update = False

        for event in pygame.event.get():
            # --- GUI BUTTONS ---
            if event.type == pygame.QUIT:
                exit_app(processor)

            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == buttons["quit"]:
                    exit_app(processor)

                if event.ui_element == buttons["start"]:
                    if is_running:
                        processor.stop()
                    try:
                        n, r, r1, r0 = (int(field.get_text()) for field in input_fields)

                        initialize_processor(n, r, r0, r1)

                        is_running = True
                        is_paused = False
                        current_frame = 0
                    except ValueError:
                        continue

                if event.ui_element == buttons["pause"] and is_running:
                    is_paused = not is_paused

                # Disable "Draw obstacles" button when animation is running
                if event.ui_element == buttons["draw_obstacles"] and not is_running:
                    drawing_obstacles = not drawing_obstacles

                if event.ui_element == buttons["chage_style"]:
                    if current_style == DrawStyle.PICTURES:
                        current_style = DrawStyle.DOTS
                    else:
                        current_style = DrawStyle.PICTURES

            manager.process_events(event)

            # --- MOUSE ---
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
                        dist = math.sqrt((start_pos[0] - end_pos[0])**2 - (start_pos[1] - end_pos[1])**2)

                        if dist > 1:
                            obstacles.append((start_pos, end_pos))  # Save the line
                        start_pos = None  # Reset the start position after drawing

        if not drawing_obstacles:
            window_surface.blit(background_surface, (0, 0))  # Redraw the background

        if is_running and not is_paused and frame_update:
            if current_frame < INTER_FRAME_NUM:
                current_coords = coords1 + delta_dist * current_frame
            else:
                raise ValueError(
                    "Current frame can't be more than the max number of frames"
                )

            draw_cats(
                coords1,
                coords2,
                current_coords,
                states1,
                window_surface,
                obstacles,
                current_style,
            )

            current_frame = current_frame + 1
            if current_frame >= INTER_FRAME_NUM:
                current_frame = 0
                coords1, states1 = coords2, states2
                coords2, states2 = processor.data.unpack()
                delta_dist = (coords2 - coords1) / INTER_FRAME_NUM

        else:
            if current_coords is not None:
                draw_cats(
                    coords1,
                    coords2,
                    current_coords,
                    states1,
                    window_surface,
                    obstacles,
                    current_style,
                )

        # Redraw all obstacles after updating the window
        for start, end in obstacles:
            pygame.draw.line(window_surface, (255, 0, 0), start, end, 2)

        pygame.display.set_caption(f"Cats  |  {math.ceil(clock.get_fps())}")
        manager.update(time_delta)
        manager.draw_ui(window_surface)
        pygame.display.update()
