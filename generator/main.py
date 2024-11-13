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
        # maximum number of trajectory repetitions
        self.__REPEATS_MAX = int(min(x_border, y_border) / (R * 2))

        # [[x_0, x_1, ...], [y_0, y_1, ...]]
        self.__cat_matrix = np.vstack((x_array, y_array))

        # every cat has its own count of trajectory repetitions
        self.__repeat_array = np.random.uniform(1, self.__REPEATS_MAX, size=(N))
        self.__angle_array = np.random.uniform(0, 360, size=(N))

    @property
    def cats(self):
        return self.__cat_matrix[0], self.__cat_matrix[1] 

    def update_cats(self):
        """Update every cat position"""
        for cat_id in range(self.__CATS_COUNT):
            self.update_cat(cat_id)
    
    def update_cat(self, cat_id: int):
        # choose trajectory for cat
        angle = self.choose_angle(cat_id)
        # move cat to a new coordinates
        self.move_cat(cat_id, angle)
        # fix cat in playing field
        self.restrict_cat(cat_id)

    def choose_angle(self, cat_id: int):
        if self.__repeat_array[cat_id] <= 0:
            self.__repeat_array[cat_id] = random.randint(1, self.__REPEATS_MAX)
            self.__angle_array = np.random.uniform(0, 360, size=(self.__CATS_COUNT))

        self.__repeat_array[cat_id] -= 1
        return self.__angle_array[cat_id]


    def move_cat(self, cat_id: int, angle: float):
        x, y = self.__cat_matrix[0][cat_id], self.__cat_matrix[1][cat_id]

        angle_in_radians = math.radians(angle)
        new_x = x + self.__RADIUS * math.cos(angle_in_radians)
        new_y = y + self.__RADIUS * math.sin(angle_in_radians)

        self.__cat_matrix[0][cat_id], self.__cat_matrix[1][cat_id] = new_x, new_y

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

# gen = CatGenerator(N=5*(10**5), R=300,x_border=10000, y_border=10000)
# xs, ys = gen.cats
# gen.update_cats()

x_border, y_border = 1000, 1000

gen = CatGenerator(N=5*(10), R=100,x_border=x_border, y_border=y_border)

for i in range(10):
    xs, ys = gen.cats

    plt.axis([0, x_border, 0, y_border])
    plt.scatter(xs, ys, c='blue')
    plt.title('Cats !!!')

    plt.savefig(f'{i}.png')
    plt.close()
    gen.update_cats()