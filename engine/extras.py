__author__ = 'MeltedHyperion7'

from enum import IntEnum


num_set = {1, 2, 3, 4, 5, 6, 7, 8, 9}


def generate_grid():
    g = []
    emp_col = [None]*9
    for i in range(9):
        g.append(list(emp_col))

    return g


class Methods(IntEnum):
    SINGLE_POS = 1
    UNIQUE_POS = 2
