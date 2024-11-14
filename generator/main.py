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

        angle_array = np.random.uniform(0, 6.28, size=(N))
        self.__angle_array_cos = np.cos(angle_array)
        self.__angle_array_sin = np.sin(angle_array)


    @property
    def cats(self):
        return self.__cat_matrix[0], self.__cat_matrix[1] 

    def update_cats(self):
        """Update every cat position"""
        self.update_angles()
        self.move_cats()
        self.restrict_cats()

    def update_angles(self):
        # get n random cats and change their angles
        n = random.randint(0, self.__CATS_COUNT)

        cat_ids = np.random.choice(self.__CATS_COUNT, size=n, replace=False)
        rads = np.random.uniform(0, 6.28, size=(n))
        rads_cos = np.cos(rads)
        rads_sin = np.sin(rads)

        self.__angle_array_cos[cat_ids] = rads_cos
        self.__angle_array_sin[cat_ids] = rads_sin

    def move_cats(self):
        # Adjust the rotated points by the radius
        self.__cat_matrix[0] += self.__RADIUS * self.__angle_array_cos
        self.__cat_matrix[1] += self.__RADIUS * self.__angle_array_sin


    def restrict_cats(self):
        """Return back the cat that escaped abroad into the playing field."""
        x, y = self.__cat_matrix[0], self.__cat_matrix[1]

        x[x > self.__BORDER['x']] = 0
        x[x < 0] = self.__BORDER['x']

        y[y > self.__BORDER['y']] = 0
        y[y < 0] = self.__BORDER['y']

        self.__cat_matrix[0], self.__cat_matrix[1] = x, y


import time

x_border, y_border = 1000, 1000
gen = CatGenerator(N=5*(10**5), R=100,x_border=x_border, y_border=y_border)

for i in range(10):
    xs, ys = gen.cats

    start = time.perf_counter()
    gen.update_cats()

    # plt.scatter(xs, ys, c='blue')
    # plt.title('Cats !!!')

    # plt.axis([0, x_border, 0, y_border])

    # plt.savefig(f'{i}.png')
    # plt.close()
    
    print(f"{i}:{time.perf_counter() - start}")