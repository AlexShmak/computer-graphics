import pygame
from processor.processor import CatState


def load_image(image_name: str):
    return pygame.image.load(f"images/{image_name}").convert_alpha()


STATE_COLORS = {
    CatState.WALK: (65, 105, 225),
    CatState.HISS: (255, 140, 0),
    CatState.FIGHT: (255, 0, 0),
    CatState.EAT: (0, 255, 127),
    CatState.HIT: (128, 128, 128),
    CatState.SLEEP: (106, 255, 255),
}
STATE_PICTURES = {
    CatState.WALK: load_image("walk.png"),
    CatState.HISS: load_image("hiss.png"),
    CatState.FIGHT: load_image("fight.png"),
    CatState.EAT: load_image("eat.png"),
    CatState.HIT: load_image("hit.png"),
    CatState.SLEEP: load_image("sleep.png"),
}


def catstate_to_color(state_id: int):
    assert state_id in STATE_PICTURES.keys(), f"Can't find color for state {state_id}!"
    return STATE_COLORS[state_id]  # Default to white


def catstate_to_picture(state_id: int):
    assert (
        state_id in STATE_PICTURES.keys()
    ), f"Can't find picture for state {state_id}!"
    return STATE_PICTURES[state_id]
