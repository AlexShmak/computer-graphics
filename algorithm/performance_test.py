import time
import numpy as np
from algo import TaichiAlgo, BasicState
import taichi as ti

ti.init(arch=ti.gpu)

N = 500_000
D = 2
points = np.random.randint(0, 1000, size=(D, N))
s = 0
r0 = 30
r1 = 50
algo = TaichiAlgo(1000, 1000, N, r0, r1, 400)
times = 7

for i in range(times):
    start = time.perf_counter()
    states = np.random.randint(1, 5, size=(N))
    algo.get_states(points, states)

    finish = time.perf_counter()

    s += finish - start
    print("Время работы: " + str(finish - start))

average_time = s / times
print("\n Среднее время: " + str(average_time))
