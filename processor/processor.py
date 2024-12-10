from algorithm.algo import AbstractAlgo, BasicState
from generator.generator import AbstractCatGenerator
import multiprocessing as mp
import numpy as np


class CatState(BasicState):
    EAT = 4
    HIT = 5
    SLEEP = 6


class CatProcessor:
    """Split work between cat generator and the algorithm for processing them."""

    def __init__(
        self, algo: AbstractAlgo, gen: AbstractCatGenerator, MAX_SIZE: int = 10
    ):
        self.__algo = algo
        self.__gen = gen

        # init queues
        self.__gen_queue = mp.Queue(MAX_SIZE)
        self.__algo_queue = mp.Queue(MAX_SIZE)

        # start workers
        self.__start_workers()

    @property
    def bank_size(self):
        return self.__algo_queue.qsize()

    @property
    def data(self):
        return self.__algo_queue.get()
    
    def stop(self):
        self.__gen_proc.join()
        self.__algo_proc.join()

        self.__gen_proc.close()
        self.__algo_proc.close()

    def __start_workers(self):
        self.__gen_proc = mp.Process(target=self.__gen_worker, args=(self.__gen.N, self.__gen_queue, self.__gen))
        self.__algo_proc = mp.Process(
            target=self.__algo_worker, args=(self.__gen_queue, self.__algo_queue, self.__algo)
        )

        self.__gen_proc.start()
        self.__algo_proc.start()

    def __gen_worker(self, N: int, q: mp.Queue, gen: AbstractCatGenerator):
        while True:
            # get new cat positions
            gen.update_cats()
            cats = gen.cats

            # form states array
            states = np.full(N, CatState.WALK)

            if gen.sleepy_cat_ids.size > 0:
                states[gen.sleepy_cat_ids] = CatState.SLEEP
            if gen.hit_cat_ids.size > 0:
                states[gen.hit_cat_ids] = CatState.HIT
            if gen.eating_cat_ids.size > 0:
                states[gen.eating_cat_ids] = CatState.EAT

            # add states array to cats array
            cats_with_states = np.vstack((cats, states))

            # put data for algo
            q.put(cats_with_states)

    def __algo_worker(self, q_get: mp.Queue, q_put: mp.Queue, algo: AbstractAlgo):
        while True:
            cats_with_states = q_get.get()

            # unpacking
            cats = cats_with_states[:2, :]
            states = cats_with_states[2, :]

            # replace empty states with new algo states
            empty_indices = states == CatState.WALK
            states[empty_indices] = algo.get_states(cats)[empty_indices]

            # pack
            result = np.vstack((cats, states))

            # put data for output
            q_put.put(result)
