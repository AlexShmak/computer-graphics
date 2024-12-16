from abc import abstractmethod
import taichi as ti
import numpy as np
from numpy.typing import NDArray


class BasicState:
    WALK = 1
    HISS = 2
    FIGHT = 3


class AbstractAlgo:
    """An algorithm that processes cats and returns their states."""

    @abstractmethod
    def get_states(self, cat_pos, out_states):
        """Process cats and return their states."""
        pass


@ti.data_oriented
class TaichiAlgo(AbstractAlgo):
    def __init__(
        self,
        X_border: ti.f32,
        Y_border: ti.f32,
        N: ti.i32,
        R0: ti.f32,
        R1: ti.f32,
        limit_per_cell: int = 400,
    ):
        self.N = N
        self.R0 = R0
        self.R1 = R1

        self.limit_per_cell = limit_per_cell

        self.cell_size = self.R1
        self.cell_Xn = int(X_border / self.cell_size) + 1
        self.cell_Yn = int(Y_border / self.cell_size) + 1

        self.cats_per_cell = ti.field(
            dtype=ti.i32, shape=(self.cell_Xn, self.cell_Yn)
        )
        self.column_sum = ti.field(dtype=ti.i32, shape=self.cell_Xn)
        self.prefix_sum = ti.field(
            dtype=ti.i32, shape=(self.cell_Xn, self.cell_Yn)
        )
        self.list_head = ti.field(dtype=ti.i32, shape=self.cell_Xn * self.cell_Yn)
        self.list_cur = ti.field(dtype=ti.i32, shape=self.cell_Xn * self.cell_Yn)
        self.list_tail = ti.field(dtype=ti.i32, shape=self.cell_Xn * self.cell_Yn)
        self.cats_id = ti.field(dtype=ti.i32, shape=self.N)

    @ti.kernel
    def get_states(self, cat_pos: ti.types.ndarray(), out_states: ti.types.ndarray()):

        self.cats_per_cell.fill(0)
        for i in range(self.N):
            x_idx = ti.floor(cat_pos[0, i] / self.cell_size, int)
            y_idx = ti.floor(cat_pos[1, i] / self.cell_size, int)
            ti.atomic_add(self.cats_per_cell[x_idx, y_idx], 1)

        for i in range(self.cell_Xn):
            cur_sum = 0
            for j in range(self.cell_Yn):
                cur_sum += self.cats_per_cell[i, j]
            self.column_sum[i] = cur_sum

        self.prefix_sum[0, 0] = 0
        ti.loop_config(serialize=True)
        for i in range(1, self.cell_Xn):
            self.prefix_sum[i, 0] = (
                self.prefix_sum[i - 1, 0] + self.column_sum[i - 1]
            )

        for i in range(self.cell_Xn):
            for j in range(self.cell_Yn):
                if j == 0:
                    self.prefix_sum[i, j] += self.cats_per_cell[i, j]
                else:
                    self.prefix_sum[i, j] = (
                        self.prefix_sum[i, j - 1] + self.cats_per_cell[i, j]
                    )

                linear_idx = i * self.cell_Yn + j
                self.list_head[linear_idx] = (
                    self.prefix_sum[i, j] - self.cats_per_cell[i, j]
                )
                self.list_cur[linear_idx] = self.list_head[linear_idx]
                self.list_tail[linear_idx] = self.prefix_sum[i, j]

        for i in range(self.N):
            x_idx = ti.floor(cat_pos[0, i] / self.cell_size, int)
            y_idx = ti.floor(cat_pos[1, i] / self.cell_size, int)
            linear_idx = x_idx * self.cell_Yn + y_idx
            cell_location = ti.atomic_add(self.list_cur[linear_idx], 1)
            self.cats_id[cell_location] = i

        for i in range(self.N):
            if out_states[i] != BasicState.WALK and out_states[i] != BasicState.HISS and out_states[i] != BasicState.FIGHT:
                continue  

            x_idx = ti.floor(cat_pos[0, i] / self.cell_size, int)
            y_idx = ti.floor(cat_pos[1, i] / self.cell_size, int)
            x_begin = max(x_idx - 1, 0)
            x_end = min(x_idx + 2, self.cell_Xn)
            y_begin = max(y_idx - 1, 0)
            y_end = min(y_idx + 2, self.cell_Yn)

            state = BasicState.WALK
            for neigh_x in range(x_begin, x_end):
                for neigh_y in range(y_begin, y_end):
                    neigh_linear_idx = neigh_x * self.cell_Yn + neigh_y
                    processed = 0
                    for p in range(
                        self.list_head[neigh_linear_idx],
                        self.list_tail[neigh_linear_idx],
                    ):
                        if processed > self.limit_per_cell:
                            break
                        processed += 1
                        j = self.cats_id[p]
                        if i != j:
                            dist = ti.sqrt(
                                (cat_pos[0, i] - cat_pos[0, j]) ** 2
                                + (cat_pos[1, i] - cat_pos[1, j]) ** 2
                            )
                            if dist <= self.R0:
                                state = BasicState.FIGHT
                                break
                            elif dist <= self.R1:
                                prob = 1.0 / (dist * dist)
                                if ti.random() <= prob:
                                    state = BasicState.HISS
                    if state == BasicState.FIGHT:
                        break
                if state == BasicState.FIGHT:
                    break

            out_states[i] = state