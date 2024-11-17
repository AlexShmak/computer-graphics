import time
import numpy as np
from common import WALK
from states_update import update_states, N, D

points = np.random.randint(0, 10000, size=(D, N))
st = np.full(N, WALK, dtype=np.uint8)
states = [st.copy() for _ in range(7)]

r0 = 3
r1 = 6
for i in range(7):
    start = time.perf_counter()
    update_states(points, r0, r1, states[i])

    finish = time.perf_counter()

    print('Время работы: ' + str(finish - start))
