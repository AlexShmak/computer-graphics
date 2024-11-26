import sys
import os
import pytest
import numpy as np

sys.path.append(os.getcwd())

from algorithm.common import FIGHT, HISS, WALK
from algorithm.states_updater import update_states


@pytest.fixture
def default_params():
    return {"r0": 2, "r1": 4, "num_points": 5}


def test_all_fight(default_params):
    r0, r1, num_points = (
        default_params["r0"],
        default_params["r1"],
        default_params["num_points"],
    )
    coords = np.array([[0, 1, 2, 3, 4], [0, 1, 2, 3, 4]])
    states = np.array([WALK] * num_points)
    update_states(coords, r0, r1, states)
    assert all(state == FIGHT for state in states)


def test_all_walk(default_params):
    r0, r1, num_points = (
        default_params["r0"],
        default_params["r1"],
        default_params["num_points"],
    )
    coords = np.array([[0, 5, 9, 16, 20], [0, 5, 9, 16, 20]])
    states = np.array([FIGHT] * num_points)
    update_states(coords, r0, r1, states)
    print(states)
    assert all(state == WALK for state in states)


def test_mixed_states(default_params):
    r0, r1, num_points = (
        default_params["r0"],
        default_params["r1"],
        default_params["num_points"],
    )
    coords = np.array([[0, 1, 4, 9, 15], [0, 1, 4, 9, 15]])
    states = np.array([WALK] * num_points)
    update_states(coords, r0, r1, states)

    assert states[0] == FIGHT
    assert states[1] == FIGHT
    assert states[2] in [HISS, WALK]
    assert states[3] == WALK
    assert states[4] == WALK
