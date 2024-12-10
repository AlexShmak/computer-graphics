import numpy as np
from numpy.typing import NDArray


class BasicState:
    Walk = 1
    Hiss = 2
    Fight = 3


def get_fake_states(cat_pos: NDArray):
    N = cat_pos[0].shape[0]
    states = np.random.choice([BasicState.Walk, BasicState.Hiss, BasicState.Fight], size=N)

    return states 