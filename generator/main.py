from turtle import update
import numpy as np
import matplotlib.pyplot as plt
import random
import multiprocessing
import math

class CatGenerator:
    def __init__(self, N, R, x_border, y_border):
        assert R < x_border and R < y_border

        x_array = np.random.uniform(0, x_border, size=(N))
        y_array = np.random.uniform(0, y_border, size=(N))

        self.__CATS_COUNT = N
        self.__BORDER = {'x': x_border, 'y': y_border}
        self.__RADIUS = R

        # [[x_0, x_1, ...], [y_0, y_1, ...]]
        self.__cat_matrix = np.vstack((x_array, y_array))

        self.__angle_array = np.random.uniform(0, 6.28, size=(N))
        self.__angle_array_cos = np.cos(self.__angle_array)
        self.__angle_array_sin = np.sin(self.__angle_array)


    @property
    def cats(self):
        return self.__cat_matrix[0], self.__cat_matrix[1] 

    def update_cats(self):
        """Update every cat position"""
        self.update_angles()
        self.move_cats()

        for cat_id in range(self.__CATS_COUNT):
            self.restrict_cat(cat_id)


    def update_angles(self):
        # get n random cats and change their angles
        n = random.randint(0, self.__CATS_COUNT)

        cat_ids = np.random.choice(self.__CATS_COUNT, size=n, replace=False)
        rads = np.random.uniform(0, 6.28, size=(n))
        rads_cos = np.cos(rads)
        rads_sin = np.sin(rads)

        self.__angle_array[cat_ids] = rads
        self.__angle_array_cos[cat_ids] = rads_cos
        self.__angle_array_sin[cat_ids] = rads_sin

    def move_cats(self):
        # Adjust the rotated points by the radius
        self.__cat_matrix[0] += self.__RADIUS * self.__angle_array_cos
        self.__cat_matrix[1] += self.__RADIUS * self.__angle_array_sin


    def restrict_cat(self, cat_id: int):
        """Return back the cat that escaped abroad into the playing field."""
        x, y = self.__cat_matrix[0][cat_id], self.__cat_matrix[1][cat_id]
        new_x, new_y = x, y

        if x > self.__BORDER['x']:
            new_x = 0 
        elif y > self.__BORDER['y']:
            new_y = 0
        elif x < 0:
            new_x = self.__BORDER['x']
        elif y < 0:
            new_y = self.__BORDER['y']
        else:
            return
        
        self.__cat_matrix[0][cat_id], self.__cat_matrix[1][cat_id] = new_x, new_y


import time
x_border, y_border = 1000, 1000
gen = CatGenerator(N=5*(10**5), R=100,x_border=x_border, y_border=y_border)

for i in range(10):
    xs, ys = gen.cats

    start = time.perf_counter()
    gen.update_cats()
    print(time.perf_counter() - start)