import numpy as np

WALK = 0
HISS = 1
FIGHT = 2
SLEEP = 3
EAT = 4
HIT = 5

def calculate(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))

class StatesUpdater:
    def __init__(self, X, Y, N, R0, R1, cats, states):
        self.X = X
        self.Y = Y
        self.N = N
        self.R0 = R0
        self.R1 = R1
        self.cats = cats
        self.states = states
        self.cell_Xn = X // R1 + 1
        self.cell_Yn = Y // R1 + 1
        self.cats_per_cell = np.zeros((self.cell_Xn, self.cell_Yn), dtype=np.int32)
        self.cats_idx = np.arange(N, dtype=np.int32)
        self.list_head = np.empty(self.cell_Xn*self.cell_Yn, dtype=np.int32)
        self.list_cur = np.empty(self.cell_Xn*self.cell_Yn, dtype=np.int32)
        self.list_tail = np.empty(self.cell_Xn*self.cell_Yn, dtype=np.int32)
    
    def update(self):
        self.cats_per_cell.fill(0)
        for i in range(self.N):
            x_idx = self.cats[0, i] // self.R1
            y_idx = self.cats[1, i] // self.R1
            self.cats_per_cell[x_idx, y_idx] += 1
        
        s = 0
        for i in range(self.cell_Xn):
            for j in range(self.cell_Yn):
                idx = i * self.cell_Yn + j
                self.list_head[idx] = s
                self.list_cur[idx] = s
                self.list_tail[idx] = s + self.cats_per_cell[i,j]
                s += self.cats_per_cell[i,j]
        
        for i in range(self.N):
            x_idx = self.cats[0, i] // self.R1
            y_idx = self.cats[1, i] // self.R1
            lin_idx = x_idx * self.cell_Yn + y_idx
            cell = self.list_cur[lin_idx]
            self.list_cur[lin_idx] += 1
            self.cats_idx[cell] = i

        for i in range(self.N):
            x_idx = self.cats[0, i] // self.R1
            y_idx = self.cats[1, i] // self.R1
            x_begin = max(x_idx - 1, 0)
            x_end = max(x_idx + 2, self.cell_Xn)
            y_begin = max(y_idx - 1, 0)
            y_end = max(y_idx + 2, self.cell_Yn)

            for neigh_x in range(x_begin, x_end):
                for neigh_y in range(y_begin, y_end):
                    lin_idx = neigh_x * self.cell_Yn + neigh_y
                    for p in range(self.list_head[lin_idx], self.list_tail[lin_idx]):
                        j = self.cats_idx[p]
                        if i != j:
                            dist = calculate(self.cats[0,i], self.cats[1,i], self.cats[0,j], self.cats[1,j])
                            if dist <= self.R0:
                                self.states[i] = FIGHT
                            elif dist <= self.R1:
                                prob = 1.0/(dist*dist)
                                if np.random.rand() <= prob:
                                    self.states[i] = HISS
                                else:
                                    self.states[i] = WALK
                            else:
                                self.states[i] = WALK