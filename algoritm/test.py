import time
import numpy as np
from states_update import update_states

points = np.random.randint(0, 10000, size=(5*10**4, 2))
r0 = 3
r1 = 6
for i in range(7):
    start = time.perf_counter()
    res = update_states(points, r0, r1)

    finish = time.perf_counter()

    print('Время работы: ' + str(finish - start))
