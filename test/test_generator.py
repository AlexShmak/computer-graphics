from time import perf_counter
import pytest
from generator.generator import CatGenerator
import random


@pytest.fixture(
    params=[
        (500, 100, 1000, 1000),  # N, R, Borders
        (5000, 100, 1000, 1000),
        (50000, 300, 5000, 5000),
        (500000, 300, 5000, 5000),
    ],
    scope="function",
)
def cat_generator(request):
    N, R, X_BORDER, Y_BORDER = request.param

    return CatGenerator(N=N, R=R, x_border=X_BORDER, y_border=Y_BORDER)


def test_speed(cat_generator: CatGenerator):
    """Test performance for all data sets."""
    start = perf_counter()
    cat_generator.update_cats()
    end = perf_counter()

    assert start - end <= 0.5


def test_cats_count(cat_generator: CatGenerator):
    """Check that cats don't disappear when generated."""
    start_len = len(cat_generator.cats[0])

    for _ in range(10):
        cat_generator.update_cats()
        assert len(cat_generator.cats[0]) == start_len


def test_random_bad_borders(cat_generator: CatGenerator):
    """Check that cats can hit walls."""
    # Generate random borders
    for _ in range(10):
        cat_generator.add_bad_border(
            (random.randint(0, 1000), random.randint(0, 1000)),
            (random.randint(0, 1000), random.randint(0, 1000)),
        )

    # Move cats
    cat_generator.update_cats()

    # approximate number of hit cats
    assert len(cat_generator.hit_cat_ids) > 10


def test_bad_borders_time_limitations(cat_generator: CatGenerator):
    """Check perfomance of map with borders."""
    for _ in range(10):
        cat_generator.add_bad_border(
            (random.randint(0, 1000), random.randint(0, 1000)),
            (random.randint(0, 1000), random.randint(0, 1000)),
        )

    # Move cats
    start = perf_counter()
    cat_generator.update_cats()
    end = perf_counter()

    # approximate number of hit cats
    assert end - start <= 0.5


def test_food_spawn(cat_generator: CatGenerator):
    """Checks that the amount of food always remains the same."""
    start_food_count = len(cat_generator.food)

    for _ in range(10):
        cat_generator.update_cats()

    assert start_food_count == len(cat_generator.food)


def test_eating_cats_count(cat_generator: CatGenerator):
    """Check that cats can eat food."""
    # Move cats
    cat_generator.update_cats()

    # approximate number of eating cats
    assert len(cat_generator.eating_cat_ids) > 10
