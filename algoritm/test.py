import time
import numpy as np
from states_update import update_states, N, D

points = np.random.randint(0, 10000, size=(N, D))
r0 = 3
r1 = 6
for i in range(7):
    start = time.perf_counter()
    res = update_states(points, r0, r1)

    finish = time.perf_counter()

    print('Время работы: ' + str(finish - start))
