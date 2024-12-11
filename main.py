from algorithm.algo import FakeCatAlgo
from generator.generator import CatGenerator
from processor.processor import CatProcessor, CatState
import time
import numpy as np

N = 500_000
gen = CatGenerator(N, 100, 10000, 10000)
algo = FakeCatAlgo()

proc = CatProcessor(algo, gen)
time.sleep(0.5)


for _ in range(10):
    print('Bank size:', proc.bank_size)

    data = proc.data

    cats, states = data.unpack()
    print('Eating cats:', np.count_nonzero(states == CatState.EAT))
    print('Hit cats:', np.count_nonzero(states == CatState.HIT))
    print('Sleep cats:', np.count_nonzero(states == CatState.SLEEP))
    print()

print('Stopping ...')
proc.stop()
