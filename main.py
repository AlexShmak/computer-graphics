from algorithm.algo import TaichiAlgo
from generator.generator import CatGenerator
from processor.processor import CatProcessor, CatState
import multiprocessing as mp
import time
import numpy as np
import taichi as ti

N = 500_000
X_BORDER, Y_BORDER = 1000, 1000

gen = CatGenerator(N, 100, X_BORDER, Y_BORDER)
algo = TaichiAlgo(X_BORDER, Y_BORDER, N, R0=30, R1=25)

proc = CatProcessor(algo, gen, workers_count=2)
proc.start()

for _ in range(10):
    print("Bank size:", proc.bank_size)

    cats, states, food = proc.data.unpack()
    print("Food: ", food.size)
    print("Eating cats:", np.count_nonzero(states == CatState.EAT))
    print("Hit cats:", np.count_nonzero(states == CatState.HIT))
    print("Sleeping cats:", np.count_nonzero(states == CatState.SLEEP))
    print("Walking cats:", np.count_nonzero(states == CatState.WALK))
    print("Hissing cats:", np.count_nonzero(states == CatState.HISS))
    print("Fighting cats:", np.count_nonzero(states == CatState.FIGHT))
    print()


print("Stopping ...")
proc.stop()
