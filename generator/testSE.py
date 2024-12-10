import random
from generator import CatGenerator

x = 100
y = 100

def test_cat_movement_within_borders(cat_generator: CatGenerator):
    cat_generator.update_cats()
    for cat in cat_generator.cats:
        assert 0 <= cat[0] <= x
        assert 0 <= cat[1] <= y

def test_cats_avoid_walls(cat_generator: CatGenerator):
    for _ in range(5):
        cat_generator.add_bad_border(
            (random.randint(0, 1000), random.randint(0, 1000)),
            (random.randint(0, 1000), random.randint(0, 1000)),
        )

    cat_generator.update_cats()
    assert len(cat_generator.hit_cat_ids) == 0
    
def test_cat_respawn_after_eating(cat_generator: CatGenerator):
    start_positions = [(cat[0], cat[1]) for cat in cat_generator.cats]
    cat_generator.update_cats()
    for i, _ in enumerate(cat_generator.cats):
        if id in cat_generator.eating_cat_ids:
            assert (cat_generator.cats[id][0], cat_generator.cats[id][1]) != start_positions[i]
    
cat = CatGenerator(5, 10, x, y)
test_cat_movement_within_borders(cat)
test_cats_avoid_walls(cat)
test_cat_respawn_after_eating(cat)
