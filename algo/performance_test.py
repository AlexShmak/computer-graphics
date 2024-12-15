import time
import sys
import os
import numpy as np


from states_updater import *

N = 10 * 10**5
D = 2
points = np.random.randint(0, 1000, size=(D, N))
st = np.full(N, WALK, dtype=np.uint8)
states = [st.copy() for _ in range(7)]

s = 0
r0 = 30
r1 = 50
init_updater(1000,1000, N, r0, r1)
times = 7
for i in range(times):
    start = time.perf_counter()
    states_updater(points, states[i])

    finish = time.perf_counter()

    s += finish - start
    print("Время работы: " + str(finish - start))
average_time = s / times

print("\n Среднее время: " + str(average_time))
