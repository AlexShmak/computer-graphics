from abc import abstractmethod
import numpy as np
from numpy.typing import NDArray


class BasicState:
    WALK = 1
    HISS = 2
    FIGHT = 3


class AbstractAlgo:
    """An algorithm that processes cats and returns their states."""

    @abstractmethod
    def get_states(self, cat_pos: NDArray):
        """Process cats and return their states."""
        pass


class FakeCatAlgo(AbstractAlgo):
    """Fake algo just for testing purposes."""

    def get_states(self, cat_pos):
        N = cat_pos[0].shape[0]
        states = np.random.choice(
            [BasicState.WALK, BasicState.HISS, BasicState.FIGHT], size=N
        )

        return states
