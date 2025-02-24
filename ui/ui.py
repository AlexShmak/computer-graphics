"""Graphical User Interface (GUI) Module for Cats App"""

import math
import os
import sys

# from time import perf_counter
import pygame
import pygame_gui

sys.path.append(os.getcwd())

from algorithm.algorithm import CatAlgorithm, DistanceFunction
from generator.generator import CatGenerator
from processor.processor import CatProcessor, CatState
from ui.cat_drawer import RES, DrawStyle, draw_cats
from ui.resources import init_pygame_pictures

INTER_FRAME_NUM = 60  # Number of interpolated frames
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

    def create_button(text, pos, width=300, height=50):
        return pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(pos, (width, height)),
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
        "euclidian_dist_fun": create_button("Euclidian", (50, 520), width=98),
        "manhattan_dist_fun": create_button("Manhattan", (151, 520), width=98),
        "chebyshev_dist_fun": create_button("Chebyshev", (252, 520), width=98),
        "quit": create_button("Quit", (50, 580)),
    }

    # State Variables
    is_running = False
    is_paused = False
    current_frame = 0
    current_style = DrawStyle.PICTURES

    generator: CatGenerator = None
    algorithm: CatAlgorithm = None
    processor: CatProcessor = None

    coords1, states1, coords2, states2, food1, food2, current_coords = (
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
    delta_dist = None

    # Obstacle variables
    obstacles = []
    drawing_obstacles = False
    start_pos = None

    # Frames update
    # last_frame_time = 0

    def initialize_processor(n, r, r0, r1, dist_fun=DistanceFunction.EUCLIDEAN):
        nonlocal \
            generator, \
            processor, \
            coords1, \
            states1, \
            coords2, \
            states2, \
            food1, \
            food2, \
            delta_dist
        generator = CatGenerator(n, r, *RES)
        for obstacle in obstacles:
            generator.add_bad_border(obstacle[0], obstacle[1])
        algorithm = CatAlgorithm(*RES, n, r0, r1, distance_fun=dist_fun)
        processor = CatProcessor(algorithm, generator)
        processor.start()

        coords1, states1, food1 = processor.data.unpack()
        coords2, states2, food2 = processor.data.unpack()

        delta_dist = (coords2 - coords1) / INTER_FRAME_NUM

    def start_animation(dis_fun: DistanceFunction = DistanceFunction.EUCLIDEAN):
        nonlocal is_running, is_paused, current_frame, drawing_obstacles
        global INTER_FRAME_NUM
        if is_running:
            processor.stop()
        try:
            n, r, r1, r0 = (int(field.get_text()) for field in input_fields)
            INTER_FRAME_NUM = get_inter_frame_num(n)

            initialize_processor(n, r, r0, r1)

            is_running = True
            is_paused = False
            current_frame = 0
            drawing_obstacles = False
        except ValueError as e:
            print(repr(e))

    # Main Loop
    while True:
        time_delta = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            # --- GUI BUTTONS ---
            if event.type == pygame.QUIT:
                exit_app(processor)

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == buttons["quit"]:
                    exit_app(processor)

                if event.ui_element == buttons["start"]:
                    start_animation()

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
                if is_running:
                    if event.ui_element == buttons["euclidian_dist_fun"]:
                        start_animation(DistanceFunction.EUCLIDEAN)

                    if event.ui_element == buttons["manhattan_dist_fun"]:
                        start_animation(DistanceFunction.MANHATTAN)

                    if event.ui_element == buttons["chebyshev_dist_fun"]:
                        start_animation(DistanceFunction.CHEBYSHEV)

            # --- MOUSE ---
            if drawing_obstacles and not is_running:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    start_pos = event.pos
                elif event.type == pygame.MOUSEMOTION and start_pos:
                    end_pos = event.pos

                elif event.type == pygame.MOUSEBUTTONUP and start_pos:
                    end_pos = event.pos
                    dist = math.sqrt(
                        (start_pos[0] - end_pos[0]) ** 2
                        + (start_pos[1] - end_pos[1]) ** 2
                    )
                    if dist > 1:
                        obstacles.append((start_pos, end_pos))
                    start_pos = None

            manager.process_events(event)

        # Clear the screen
        window_surface.blit(background_surface, (0, 0))

        # Draw dynamically if in obstacle drawing mode
        if drawing_obstacles and start_pos:
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.line(window_surface, (255, 200, 200), start_pos, mouse_pos, 2)

        # Draw existing obstacles
        for start, end in obstacles:
            pygame.draw.line(window_surface, (255, 0, 0), start, end, 2)

        if is_running and not is_paused:
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
                food1,
                current_style,
            )

            current_frame = current_frame + 1
            if current_frame >= INTER_FRAME_NUM:
                current_frame = 0
                coords1, states1, food1 = coords2, states2, food2
                coords2, states2, food2 = processor.data.unpack()

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
                    food1,
                    current_style,
                )

        # Redraw all obstacles after updating the window
        for start, end in obstacles:
            pygame.draw.line(window_surface, (255, 0, 0), start, end, 2)

        pygame.display.set_caption(f"Cats  |  {math.ceil(clock.get_fps())}")
        manager.update(time_delta)
        manager.draw_ui(window_surface)
        pygame.display.update()


def get_inter_frame_num(N):
    return (
        (N >= 400_000) * 1
        + ((N >= 100_000) and (N < 400_000)) * 30
        + (N < 100_000) * 60
    )
