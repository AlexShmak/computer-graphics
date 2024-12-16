import time
import numpy as np
from algo import TaichiAlgo
import taichi as ti
import pytest

@pytest.fixture(
    params=[
        (500, 1000, 1000, 15, 25),  # N, Borders, R0, R1
        (5000, 1000, 1000, 15, 25),
        (50_000, 5000, 5000, 30, 50),
        (500_000, 5000, 5000, 30, 50),
    ],
    scope="function",
)
def algo(request):
    N, X_BORDER, Y_BORDER, R0, R1 = request.param

    return TaichiAlgo(X_BORDER, Y_BORDER, N, R0, R1)

def test_performance(algo: TaichiAlgo):
    ti.init(arch=ti.gpu)

    points = np.random.randint(0, 1000, size=(2, algo.N))
    algo.start()

    time_sum = 0
    times = 7

    for _ in range(times):
        start = time.perf_counter()
        states = np.random.randint(1, 5, size=(algo.N))
        algo.get_states(points, states)
        finish = time.perf_counter()

        time_sum += finish - start

    average_time = time_sum / times
    assert average_time <= 0.5, "Too slow :("