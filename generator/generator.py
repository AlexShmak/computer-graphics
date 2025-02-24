from abc import abstractmethod
import random
from typing import Tuple

import numpy as np


class AbstractCatGenerator:
    @property
    @abstractmethod
    def N(self):
        pass

    @property
    @abstractmethod
    def cats(self):
        pass

    @property
    @abstractmethod
    def hit_cat_ids(self):
        pass

    @property
    @abstractmethod
    def sleepy_cat_ids(self):
        pass

    @property
    @abstractmethod
    def eating_cat_ids(self):
        pass

    @property
    @abstractmethod
    def food(self):
        pass

    @abstractmethod
    def update_cats(self):
        pass

    @abstractmethod
    def add_bad_border(self, a: Tuple[int, int], b: Tuple[int, int]):
        pass


class CatGenerator(AbstractCatGenerator):
    def __init__(self, N, R, x_border, y_border):
        assert R < x_border and R < y_border

        # random cat coordinates
        x_array = np.random.uniform(0, x_border, size=(N))
        y_array = np.random.uniform(0, y_border, size=(N))

        self.__CATS_COUNT = N
        self.__BORDER = {"x": x_border, "y": y_border}
        self.__RADIUS = R
        self.__FOOD_COUNT = 10  # number of food pieces on the map at the same time
        self.__FOOD_SMELL_RADIUS = self.__RADIUS

        # [[x_0, x_1, ...], [y_0, y_1, ...]]
        self.__cat_coordinates = np.vstack((x_array, y_array))

        self.__hit_cat_ids = np.array([])
        self.__sleepy_cat_ids = np.array([])
        self.__eating_cat_ids = np.array([])

        x_food_coordinates = np.random.uniform(0, x_border, size=(self.__FOOD_COUNT))
        y_food_coordinates = np.random.uniform(0, y_border, size=(self.__FOOD_COUNT))
        self.__food_coordinates = np.vstack((x_food_coordinates, y_food_coordinates))

        angle_array = np.random.uniform(0, 6.28, size=(N))
        self.__cos_array = np.cos(angle_array)
        self.__sin_array = np.sin(angle_array)

        self.__bad_border_coordinates = []

    @property
    def N(self):
        return self.__CATS_COUNT

    @property
    def cats(self):
        return self.__cat_coordinates

    @property
    def hit_cat_ids(self):
        return self.__hit_cat_ids.astype(int)

    @property
    def sleepy_cat_ids(self):
        return self.__sleepy_cat_ids.astype(int)

    @property
    def eating_cat_ids(self):
        return self.__eating_cat_ids.astype(int)

    @property
    def food(self):
        return self.__food_coordinates

    def update_cats(self):
        """Update every cat position"""
        self.__update_angles()
        self.__move_cats()
        self.__restrict_cats()

    def add_bad_border(self, a: Tuple[int, int], b: Tuple[int, int]):
        self.__bad_border_coordinates.append([*a, *b])

    def __update_angles(self):
        """Randomly updates the angles of a cats subset.

        (Only a certain number of cats can change direction each turn)
        """
        n = random.randint(0, self.__CATS_COUNT)

        cat_ids = np.random.choice(self.__CATS_COUNT, size=n, replace=False)
        rads = np.random.uniform(0, 6.28, size=(n))
        rads_cos = np.cos(rads)
        rads_sin = np.sin(rads)

        self.__cos_array[cat_ids] = rads_cos
        self.__sin_array[cat_ids] = rads_sin

    def __move_cats(self):
        """Move all cats based on their current angles."""
        xs, ys = self.__cat_coordinates[0], self.__cat_coordinates[1]
        self.__eating_cat_ids = np.array([])
        self.__hit_cat_ids = np.array([])

        ### get sleepy cats
        sleepy_cats_count = random.randint(0, self.__CATS_COUNT // 10)
        sleepy_cat_ids = np.random.choice(
            self.__cat_coordinates[0].shape[0], sleepy_cats_count, replace=False
        )
        self.__sleepy_cat_ids = sleepy_cat_ids

        # find points where cats want to move
        new_xs = xs + self.__RADIUS * self.__cos_array
        new_ys = ys + self.__RADIUS * self.__sin_array

        ### look through all the bad borders
        for x0, y0, x1, y1 in self.__bad_border_coordinates:
            # find all intersections of cats with bad border
            hit_ids, intersection_xs, intersection_ys = self.__find_intersections(
                xs, ys, new_xs, new_ys, x0, y0, x1, y1
            )
            # ids -> id of cats that tried to intersect bad border

            if hit_ids.size == 0:
                continue

            self.__hit_cat_ids = np.append(self.__hit_cat_ids, hit_ids)

            # return back these cats (but with small offset otherwise they will get stuck at the border)
            new_xs[hit_ids], new_ys[hit_ids] = self.__offset_points(
                xs[hit_ids], ys[hit_ids], intersection_xs, intersection_ys
            )

        self.__hit_cat_ids = np.unique(self.__hit_cat_ids)

        ### find eating cats
        food_xs, food_ys = self.__food_coordinates
        for food_id, (food_x, food_y) in enumerate(zip(food_xs, food_ys)):
            distances = np.sqrt(np.square(xs - food_x) + np.square(ys - food_y))
            eating_cats_mask = distances < self.__FOOD_SMELL_RADIUS

            if eating_cats_mask.size <= 0:
                continue

            # stay at the same place
            new_xs[eating_cats_mask] = xs[eating_cats_mask]
            new_ys[eating_cats_mask] = ys[eating_cats_mask]

            self.__eating_cat_ids = np.append(
                self.__eating_cat_ids, np.where(eating_cats_mask)
            )

            # relocate food
            (
                self.__food_coordinates[0, food_id],
                self.__food_coordinates[1, food_id],
            ) = (
                random.randint(0, self.__BORDER["x"]),
                random.randint(0, self.__BORDER["y"]),
            )

        self.__eating_cat_ids = np.unique(self.__eating_cat_ids)

        # put some of the cats to sleep
        new_xs[sleepy_cat_ids], new_ys[sleepy_cat_ids] = (
            xs[sleepy_cat_ids],
            ys[sleepy_cat_ids],
        )

        # updates coordinates
        self.__cat_coordinates[0], self.__cat_coordinates[1] = new_xs, new_ys

    def __offset_points(
        self, xs, ys, intersection_xs, intersection_ys, offset_factor=0.01
    ):
        offset_x = np.abs(intersection_xs - xs) * offset_factor
        offset_y = np.abs(intersection_ys - ys) * offset_factor

        new_xs = xs + offset_x
        new_ys = ys + offset_y

        return (new_xs, new_ys)

    def __restrict_cats(self):
        """Keeps all cats within the boundaries."""
        x, y = self.__cat_coordinates[0], self.__cat_coordinates[1]

        x[x > self.__BORDER["x"]] = 0
        x[x < 0] = self.__BORDER["x"]

        y[y > self.__BORDER["y"]] = 0
        y[y < 0] = self.__BORDER["y"]

        self.__cat_coordinates[0], self.__cat_coordinates[1] = x, y

    def __find_intersections(self, xs, ys, new_xs, new_ys, x0, y0, x1, y1):
        trajectories = (new_xs - xs, new_ys - ys)
        bad_zone = (x1 - x0, y1 - y0)

        denominators = (trajectories[0] * bad_zone[1]) - (trajectories[1] * bad_zone[0])

        t = np.divide(
            (x0 - xs) * bad_zone[1] - (y0 - ys) * bad_zone[0],
            denominators,
            out=np.zeros_like(denominators),
            where=denominators != 0,
        )
        u = np.divide(
            (x0 - xs) * trajectories[1] - (y0 - ys) * trajectories[0],
            denominators,
            out=np.zeros_like(denominators),
            where=denominators != 0,
        )

        mask = (t >= 0) & (t <= 1) & (u >= 0) & (u <= 1)
        ids = np.where(mask)[0]

        x = xs[ids] + t[ids] * trajectories[0][ids]
        y = ys[ids] + t[ids] * trajectories[1][ids]

        return (ids, x, y)
