from time import perf_counter
import pytest
from generator import CatGenerator
import numpy as np


@pytest.fixture(
    params=[
        (500, 100, 1000, 1000),  
        (5000, 100, 1000, 1000),
        (50000, 300, 5000, 5000),
        (500000, 300, 5000, 5000),
    ],
    scope="function",
)
def cat_generator(request):
    N, R, X_BORDER, Y_BORDER = request.param

    return CatGenerator(N=N, R=R, x_border=X_BORDER, y_border=Y_BORDER)

def test_cats_within_borders(cat_generator: CatGenerator):
    """Check that all cats stay within the defined borders."""
    x_border, y_border = cat_generator._CatGenerator__BORDER["x"], cat_generator._CatGenerator__BORDER["y"]

    for _ in range(10):  
        cat_generator.update_cats()
        cats = cat_generator.cats
        assert np.all(cats[0] >= 0) and np.all(cats[0] <= x_border)
        assert np.all(cats[1] >= 0) and np.all(cats[1] <= y_border)

def test_sleepy_cats_behavior(cat_generator: CatGenerator):
    """Check that sleepy cats do not move."""
    for _ in range(10):  
        initial_positions = np.copy(cat_generator.cats)
        cat_generator.update_cats()

        sleepy_ids = cat_generator.sleepy_cat_ids
        if len(sleepy_ids) > 0:
            assert np.allclose(
                cat_generator.cats[0][sleepy_ids], initial_positions[0][sleepy_ids]
            )
            assert np.allclose(
                cat_generator.cats[1][sleepy_ids], initial_positions[1][sleepy_ids]
            )

def test_food_repositioning(cat_generator: CatGenerator):
    """Ensure that food relocates within bounds after being consumed."""
    x_border, y_border = cat_generator._CatGenerator__BORDER["x"], cat_generator._CatGenerator__BORDER["y"]

    for _ in range(10):  
        initial_food_positions = np.copy(cat_generator.food)
        cat_generator.update_cats()

        for food_pos, initial_pos in zip(cat_generator.food.T, initial_food_positions.T):
            if not np.array_equal(food_pos, initial_pos):  
                assert 0 <= food_pos[0] <= x_border
                assert 0 <= food_pos[1] <= y_border

