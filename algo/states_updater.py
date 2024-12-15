import numpy as np
import taichi as ti

WALK = 0
HISS = 1
FIGHT = 2
SLEEP = 3
EAT = 4
HIT = 5

ti.init(arch=ti.gpu)

X = NotImplemented
Y = NotImplemented
N = NotImplemented
R0 = NotImplemented
R1 = NotImplemented
cell_size = NotImplemented
cell_Xn = NotImplemented
cell_Yn = NotImplemented

circles_per_cell = NotImplemented
column_sum = NotImplemented 
prefix_sum = NotImplemented
list_head = NotImplemented
list_cur = NotImplemented
list_tail = NotImplemented
cats_id = NotImplemented

def init_updater(
    _X: ti.f32,
    _Y: ti.f32,
    _N: ti.i32,
    _R0: ti.f32,
    _R1: ti.f32,
):
    global X, Y, N, R0, R1
    X = _X
    Y = _Y
    N = _N
    R0 = _R0
    R1 = _R1

    global cell_size, cell_Xn, cell_Yn
    cell_size = R1
    cell_Xn = int(X / cell_size) + 1
    cell_Yn = int(Y / cell_size) + 1

    global \
        cats_per_cell, \
        column_sum, \
        prefix_sum, \
        list_head, \
        list_cur, \
        list_tail, \
        cats_id
    cats_per_cell = ti.field(dtype=ti.i32, shape=(cell_Xn, cell_Yn))
    column_sum = ti.field(dtype=ti.i32, shape=cell_Xn)
    prefix_sum = ti.field(dtype=ti.i32, shape=(cell_Xn, cell_Yn))
    list_head = ti.field(dtype=ti.i32, shape=cell_Xn * cell_Yn)
    list_cur = ti.field(dtype=ti.i32, shape=cell_Xn * cell_Yn)
    list_tail = ti.field(dtype=ti.i32, shape=cell_Xn * cell_Yn)
    cats_id = ti.field(dtype=ti.i32, shape=N)

@ti.kernel
def states_updater(cats: np.ndarray, states: np.ndarray):
    cats_per_cell.fill(0)
    for i in range(N):
        x_idx = ti.floor(cats[0][i] / cell_size, int)
        y_idx = ti.floor(cats[1][i] / cell_size, int)
        ti.atomic_add(cats_per_cell[x_idx, y_idx], 1)

    for i in range(cell_Xn):
        cur_sum = 0
        for j in range(cell_Yn):
            cur_sum += circles_per_cell[i, j]
        column_sum[i] = cur_sum

    prefix_sum[0, 0] = 0
    ti.loop_config(serialize=True)
    for i in range(1, cell_Xn):
        prefix_sum[i, 0] = prefix_sum[i - 1, 0] + column_sum[i - 1]

    for i in range(cell_Xn):
        for j in range(cell_Yn):
            if j == 0:
                prefix_sum[i, j] += circles_per_cell[i, j]
            else:
                prefix_sum[i, j] = prefix_sum[i, j - 1] + circles_per_cell[i, j]

            linear_idx = i * cell_Yn + j
            list_head[linear_idx] = prefix_sum[i, j] - circles_per_cell[i, j]
            list_cur[linear_idx] = list_head[linear_idx]
            list_tail[linear_idx] = prefix_sum[i, j]

    for i in range(N):
        x_idx = ti.floor(cats[0][i] / cell_size, int)
        y_idx = ti.floor(cats[1][i] / cell_size, int)
        linear_idx = x_idx * cell_Yn + y_idx
        cell_location = ti.atomic_add(list_cur[linear_idx], 1)
        cats_id[cell_location] = i

    for i in range(N):
        x_idx = ti.floor(cats[0][i] / cell_size, int)
        y_idx = ti.floor(cats[1][i] / cell_size, int)
        x_begin = max(x_idx - 1, 0)
        x_end = min(x_idx + 2, cell_Xn)
        y_begin = max(y_idx - 1, 0)
        y_end = min(y_idx + 2, cell_Yn)

        state = WALK

        for neigh_x in range(x_begin, x_end):
            for neigh_y in range(y_begin, y_end):
                neigh_linear_idx = neigh_x * cell_Yn + neigh_y
                for p in range(
                    list_head[neigh_linear_idx], list_tail[neigh_linear_idx]
                ):
                    j = cats_id[p]
                    if i != j:
                        dist = ti.sqrt((cats[0][i]-cats[0][j])**2 + (cats[1][i]-cats[1][j])**2)  
                        if dist <= R0:
                            state = FIGHT
                            break
                        elif dist <= R1:
                            prob = 1.0 / (dist * dist)
                            if ti.random() <= prob:
                                state = HISS
                if state == FIGHT:
                    break
            if state == FIGHT:
                break
        states[i] = state