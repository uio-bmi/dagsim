import numpy as np


def square(param, add_param):
    output = np.square(param) + add_param
    output = np.round(output, decimals=1)
    return output


def printing(num, phra):
    aa = phra * num
    return aa


def get_select(counter=[0]):
    index_list = [0, 1, 2, 3, 4]
    counter[0] += 1
    return index_list[counter[0] - 1]


def get_stratify(counter=[0]):
    index_list = [0, 1, 2, 3, 4]
    counter[0] += 1
    return index_list[counter[0] - 1]


def get_missing(counter=[0]):
    index_list = [0, 1, 2, 3, 4]
    counter[0] += 1
    return index_list[counter[0] - 1]


def check_if_even_bool(n):
    return bool(n % 2 == 0)


def check_if_even_str(n):
    if n % 2 == 0:
        return "Even"
    else:
        return "Odd"
