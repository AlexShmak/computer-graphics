import pygame
from processor.processor import CatState


class FoodState(CatState):
    FOOD = 7


STATE_COLORS = {
    CatState.WALK: (65, 105, 225),
    CatState.HISS: (255, 140, 0),
    CatState.FIGHT: (255, 0, 0),
    CatState.EAT: (0, 255, 127),
    CatState.HIT: (128, 128, 128),
    CatState.SLEEP: (106, 255, 255),
    FoodState.FOOD: (255, 255, 255),
}
STATE_PICTURES = {}


def load_picture(image_name: str):
    return pygame.image.load(f"images/{image_name}").convert_alpha()


def init_pygame_pictures():
    """Loads images into memory.\n
    [!] Call only after pygame.init()
    """
    STATE_PICTURES[CatState.WALK] = load_picture("walk.png")
    STATE_PICTURES[CatState.HISS] = load_picture("hiss.png")
    STATE_PICTURES[CatState.FIGHT] = load_picture("fight.png")
    STATE_PICTURES[CatState.EAT] = load_picture("eat.png")
    STATE_PICTURES[CatState.HIT] = load_picture("hit.png")
    STATE_PICTURES[CatState.SLEEP] = load_picture("sleep.png")
    STATE_PICTURES[FoodState.FOOD] = load_picture("food.png")


def catstate_to_color(state_id: int):
    assert state_id in STATE_PICTURES.keys(), f"Can't find color for state {state_id}!"
    return STATE_COLORS[state_id]  # Default to white


def catstate_to_picture(state_id: int):
    assert len(STATE_PICTURES.keys()) > 0, (
        "Pictures dictionary is empty. Don't forget to call init_pygame_pictures()!"
    )
    assert state_id in STATE_PICTURES.keys(), (
        f"Can't find picture for state {state_id}!"
    )
    return STATE_PICTURES[state_id]
