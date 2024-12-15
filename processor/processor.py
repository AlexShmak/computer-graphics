from algorithm.algo import AbstractAlgo, BasicState
from generator.generator import AbstractCatGenerator
import multiprocessing as mp
import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass


class CatState(BasicState):
    """Represents all possible states of a cat."""

    EAT = 4
    HIT = 5
    SLEEP = 6


@dataclass
class CatData:
    """
    Data structure holding cat coordinates and their states.

    Attributes:
        coords (NDArray): Numpy array of cat coordinates.
        states (NDArray): Numpy array of cat states (ints corresponding to CatState enum).

    Methods:
        unpack(): Returns the coordinates and states as separate arrays.
    """

    coords: NDArray
    states: NDArray

    def unpack(self):
        """Unpacks the CatData into separate coordinate and state arrays."""
        return self.coords, self.states


class CatProcessor:
    """
    Manages the parallel processing of cat data.

    Use multiprocessing to separate the generation of cat data from its processing by an algorithm.
    """

    def __init__(
        self,
        algo: AbstractAlgo,
        gen: AbstractCatGenerator,
        workers_count: int = 5,
        max_size: int = 10,
    ):
        self.__algo = algo
        self.__gen = gen

        self.__stop_event = mp.Event()

        # use queues to communicate between the generator and the algorithm processes.
        self.__gen_queue = mp.Queue(max_size)
        self.__algo_queue = mp.Queue(max_size)

        self.__workers_count = workers_count

        # start workers
        self.__start_workers()

    @property
    def bank_size(self):
        """Return the number of items in the generator and algorithm queues."""
        assert (
            not self.__stop_event.is_set()
        ), "Can't get bank size when processor stopped."

        return (self.__gen_queue.qsize(), self.__algo_queue.qsize())

    @property
    def data(self):
        """Return current CatData."""
        assert not self.__stop_event.is_set(), "Can't get data when processor stopped."

        return self.__algo_queue.get()

    def stop(self):
        """Stop worker processes."""
        self.__stop_event.set()

        self.__gen_proc.kill()
        self.__gen_proc.join()

        for proc in self.__algo_proces:
            proc.kill()
            proc.join()

    def __start_workers(self):
        self.__gen_proc = mp.Process(
            target=self.__gen_worker,
            args=(self.__gen.N, self.__gen_queue, self.__gen),
            name="generator worker",
        )
        self.__gen_proc.start()

        # variable for algo workers sync
        self.__last_result_num = mp.Value("i", 0)
        self.__algo_proces: list[mp.Process] = []

        # start algo workers
        for _ in range(self.__workers_count):
            algo_proc = mp.Process(
                target=self.__algo_worker,
                args=(
                    self.__gen_queue,
                    self.__algo_queue,
                    self.__algo,
                    self.__last_result_num,
                ),
                name="algorithm worker",
            )
            algo_proc.start()

            self.__algo_proces.append(algo_proc)

    def __gen_worker(self, N: int, q: mp.Queue, gen: AbstractCatGenerator):
        data_num = 0  # last generated data number (need for sync)

        while True:
            data_num += 1

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
            cats_with_states = CatData(cats, states)

            # put data for algo
            q.put((cats_with_states, data_num))

    def __algo_worker(
        self, q_get: mp.Queue, q_put: mp.Queue, algo: AbstractAlgo, last_data_id
    ):
        while True:
            gen_worker_data = q_get.get()

            # unpacking
            cats, states = gen_worker_data[0].unpack()
            my_data_id: int = gen_worker_data[1]

            # replace empty states with new algo states
            empty_indices = states == CatState.WALK
            states[empty_indices] = algo.get_states(cats)[empty_indices]

            # pack
            result = CatData(cats, states)

            # wait until worker can put data
            while last_data_id.value != my_data_id - 1:
                pass

            # put data for output
            q_put.put(result)
            last_data_id.value += 1
