import time
import sys
import os
import numpy as np

sys.path.append(os.getcwd())

from algorithm.common import WALK
from algorithm.states_updater import update_states, D

N = 5 * 10**4

points = np.random.randint(0, 10000, size=(D, N))
st = np.full(N, WALK, dtype=np.uint8)
states = [st.copy() for _ in range(7)]

s = 0
r0 = 3
r1 = 6
times = 7
update_states(points, r0, r1, states[0])
for i in range(times):
    start = time.perf_counter()
    update_states(points, r0, r1, states[i])

    finish = time.perf_counter()

    s += (finish - start)
    print("Время работы: " + str(finish - start))
average_time = s / times

print("\n Среднее время: " + str(average_time))