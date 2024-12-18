"""Graphical User Interface (GUI) Module for Cats App"""

import os
import sys
import time

import pygame
import pygame_gui

sys.path.append(os.getcwd())

from algorithm.algorithm import CatAlgorithm
from generator.generator import CatGenerator
from processor.processor import CatProcessor


INTER_FRAME_NUM = 30  # Number of interpolated frames
# N = 1000  # Number of cat entities
DOT_SIZE = 1
RES = (2500,1300)


def index_to_color(ind: int):
    """Map state index to a color."""
    match ind:
        case 1:  # walk
            return (65, 105, 225)
        case 2:  # hiss
            return (255, 140, 0)
        case 3:  # fight
            return (255, 0, 0)
        case 4:  # eat
            return (0, 255, 127)
        case 5:  # hit
            return (128, 128, 128)
        case 6:  # sleep
            return (106, 255, 255)


def draw_dots(coords1, coords2, current_xs, current_ys, states, window_surface):
    for ind, (x, y) in enumerate(zip(current_xs, current_ys)):
        if (
            abs(coords2[0][ind] - coords1[0][ind]) >= RES[0] // 2
            or abs(coords2[1][ind] - coords1[1][ind]) >= RES[1] // 2
        ):
            pygame.draw.circle(
                window_surface,
                index_to_color(states[ind]),
                (coords2[0][ind], coords2[1][ind]),
                DOT_SIZE,
            )
            continue
        pygame.draw.circle(
            window_surface,
            index_to_color(states[ind]),
            (int(x), int(y)),
            DOT_SIZE,
        )


def run_ui():
    """Function to run Pygame GUI"""

    # Initialize Pygame
    pygame.init()

    pygame.display.set_caption("Cats")
    window_surface = pygame.display.set_mode(RES)
    background_surface = pygame.Surface(RES)
    background_surface.fill((0, 0, 0))

    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager(RES)

    # Labels
    cats_number_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((50, 25), (300, 25)),
        text="Number of cats",
        manager=manager,
    )
    travel_distance_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((50, 85), (300, 25)),
        text="Maximum travel distance",
        manager=manager,
    )
    hissing_distance_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((50, 145), (300, 25)),
        text="Cats start hissing at a distance",
        manager=manager,
    )
    fighting_distance_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((50, 205), (300, 25)),
        text="Cats start fighting at a distance",
        manager=manager,
    )

    # Input fields
    cats_number_input_field = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((50, 50), (300, 30)), manager=manager
    )
    travel_distance_input_field = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((50, 110), (300, 30)), manager=manager
    )
    hissing_distance_input_field = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((50, 170), (300, 30)), manager=manager
    )
    fighting_distance_input_field = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((50, 230), (300, 30)), manager=manager
    )

    # Buttons
    draw_obstacles_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((50, 280), (300, 50)),
        text="Draw obstacles",
        manager=manager,
    )
    start_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((50, 340), (300, 50)),
        text="Start animation",
        manager=manager,
    )
    pause_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((50, 400), (300, 50)),
        text="Pause/Resume",
        manager=manager,
    )
    quit_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((50, 460), (300, 50)),
        text="Quit",
        manager=manager,
    )

    # Flags and State Variables
    is_running = False
    is_paused = False  # New flag to track pause state
    current_frame = 0

    # Initialize main components
    generator = CatGenerator(0, 0, *RES)
    algo = CatAlgorithm(*RES, 0, 5, 10, 1000)
    processor = CatProcessor(algo, generator)

    coords1, states1 = None, None
    coords2, states2 = None, None
    delta_dist_x, delta_dist_y = None, None

    def initialize_processor(n, r, r0, r1):
        """Re-initialize processor, generator, and algorithm."""
        nonlocal \
            generator, \
            processor, \
            coords1, \
            states1, \
            coords2, \
            states2, \
            delta_dist_x, \
            delta_dist_y
        generator = CatGenerator(n, r, *RES)
        algorithm = CatAlgorithm(*RES, n, r0, r1)
        processor = CatProcessor(algorithm, generator)
        processor.start()

        # Initialize the coordinates and states
        coords1, states1 = processor.data.unpack()
        coords2, states2 = processor.data.unpack()

        # Safeguard interpolation deltas
        delta_dist_x = (coords2[0] - coords1[0]) / INTER_FRAME_NUM
        delta_dist_y = (coords2[1] - coords1[1]) / INTER_FRAME_NUM

    # Main Loop
    while True:
        time_delta = clock.tick(30)
        pygame.display.set_caption(f"Cats  |  {clock.get_fps():.2f} FPS")

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                processor.stop()
                sys.exit()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == quit_button:
                    pygame.quit()
                    processor.stop()
                    sys.exit()

                if event.ui_element == start_button:
                    try:
                        n = int(cats_number_input_field.get_text())
                        r = int(travel_distance_input_field.get_text())
                        r1 = int(hissing_distance_input_field.get_text())
                        r0 = int(fighting_distance_input_field.get_text())

                        if is_running:
                            processor.stop()
                        initialize_processor(n, r, r0, r1)
                        is_running = True
                        is_paused = False  # Ensure animation is not paused
                        current_frame = 0
                        start_time = time.perf_counter()
                    except ValueError:
                        pass

                if event.ui_element == pause_button:
                    if is_running:
                        is_paused = not is_paused  # Toggle the pause state
                        start_time = time.perf_counter()

            manager.process_events(event)

        # Background refresh
        window_surface.blit(background_surface, (0, 0))

        if is_running and not is_paused:  # Only update the animation if not paused
            # TODO: implement food coordinates in processor
            if time.perf_counter() - start_time <= 0.1:
                # Draw interpolated positions
                if current_frame < INTER_FRAME_NUM:
                    current_coords_x = coords1[0] + delta_dist_x * current_frame
                    current_coords_y = coords1[1] + delta_dist_y * current_frame
                else:
                    current_coords_x, current_coords_y = coords2[0], coords2[1]
                draw_dots(
                    coords1,
                    coords2,
                    current_coords_x,
                    current_coords_y,
                    states1,
                    window_surface,
                )
                start_time = time.perf_counter()
            else:
                continue
            # Transition to next segment after interpolation
            current_frame += 1
            if current_frame >= INTER_FRAME_NUM:
                coords1, states1 = coords2, states2
                coords2, states2 = processor.data.unpack()
                delta_dist_x = (coords2[0] - coords1[0]) / INTER_FRAME_NUM
                delta_dist_y = (coords2[1] - coords1[1]) / INTER_FRAME_NUM
                current_frame = 0
        else:
            if coords1 is not None:
                draw_dots(
                    coords1,
                    coords2,
                    current_coords_x,
                    current_coords_y,
                    states1,
                    window_surface,
                )

        # UI and Display Update
        manager.update(time_delta)
        manager.draw_ui(window_surface)
        pygame.display.update()
