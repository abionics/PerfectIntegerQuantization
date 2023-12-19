import json
import sys
import time

import numpy as np
from numba import njit

USE_LONG_DOUBLE = False
SOLVER = 'solver_v1'

FloatType = np.float64

if sys.platform == 'linux':
    sys.set_int_max_str_digits(10000)
    if USE_LONG_DOUBLE:
        SOLVER = 'solver_v2'
        FloatType = np.longdouble
        njit = lambda func: func

info = {
    'float type': FloatType.__name__,
    'njit': njit.__module__.startswith('numba'),
    'solver': SOLVER,
}
print(json.dumps(info, indent=4, ensure_ascii=False))


def k_naive(value: int, bits: int) -> FloatType:
    return (2 ** FloatType(value)) ** (1 / (2 ** bits - 1))


def calculate(
        bits: int,
        left: FloatType,
        right: FloatType,
        step: FloatType,
        finish: int,
        additional: tuple = (),
):
    s = FloatType(2 ** bits)
    solver = globals()[SOLVER]
    start_time = time.perf_counter()
    for bits in list(range(2 * bits, finish + 1, bits)) + list(additional):
        b = FloatType(2 ** bits)
        answer = solver(s, b, left, right, step)
        right = answer  # optimization, next answer always less than previous
        print(f'{bits}\t{answer}')
    duration = time.perf_counter() - start_time
    print(f'Duration: {duration:.2f} s')


@njit
def solver_v1(
        s: FloatType,
        b: FloatType,
        left: FloatType,
        right: FloatType,
        step: FloatType,
) -> FloatType:
    answer = left
    min_diff = function(left, s, b)
    for x in np.arange(left, right, step):
        diff = function(x, s, b)
        if diff < min_diff:
            answer = x
            min_diff = diff
    precision = -round(np.log10(step))
    return round(answer, precision)


# slower than solver_v1
@njit
def solver_v2(
        s: FloatType,
        b: FloatType,
        left: FloatType,
        right: FloatType,
        step: FloatType,
) -> FloatType:
    xs = np.arange(left, right, step)
    diffs = function(xs, s, b)
    index = np.argmin(diffs)
    precision = -round(np.log10(step))
    return round(xs[index], precision)


@njit
def function(x: FloatType | np.ndarray, s: FloatType, b: FloatType) -> FloatType | np.ndarray:
    return np.abs(x * (1 + 1 / x) ** (s - x - 1) - b)


def single():
    s = FloatType(2 ** 8)
    b = FloatType(2 ** 128)
    solver = globals()[SOLVER]
    start_time = time.perf_counter()
    answer = solver(
        s, b,
        left=FloatType(1),
        right=FloatType(32),
        step=FloatType(0.000001),
    )
    duration = time.perf_counter() - start_time
    print(f'Answer: {answer}')
    print(f'Duration: {duration:.2f} s')


def calculate_8bits():
    calculate(
        bits=8,
        left=FloatType(1),
        right=FloatType(32),
        step=FloatType(0.000001),
        finish=256,
    )


def calculate_16bits():
    calculate(
        bits=16,
        left=FloatType(1),
        right=FloatType(8192),
        step=FloatType(0.0001),
        finish=512,
        additional=(768,)
    )
    # set USE_LONG_DOUBLE = True
    # assert FloatType == np.longdouble
    # additional = (1024, 2048, 4096, 8192, 16384)
    # calculate(
    #     bits=16,
    #     left=FloatType(1),
    #     right=FloatType(128),
    #     step=FloatType(0.0001),
    #     finish=16,
    #     additional=additional,
    # )
    # print('K NAIVE:')
    # for value in additional:
    #     k = k_naive(value, bits=16)
    #     print(f'{value}\t{k:.16f}')


def calculate_32bits():
    calculate(
        bits=32,
        left=FloatType(1),
        right=FloatType(2 ** 28),
        step=FloatType(1),
        finish=992,
    )
    # set USE_LONG_DOUBLE = True
    # assert FloatType == np.longdouble
    # additional = (1024, 2048, 4096, 8192, 16384)
    # calculate(
    #     bits=32,
    #     left=FloatType(1),
    #     right=FloatType(2 ** 23),
    #     step=FloatType(1),
    #     finish=32,
    #     additional=(1024, 2048, 4096, 8192, 16384),
    # )
    # print('K NAIVE:')
    # for value in additional:
    #     k = k_naive(value, bits=32)
    #     print(f'{value}\t{k:.16f}')


if __name__ == '__main__':
    # single()
    calculate_8bits()
    # calculate_16bits()
    # calculate_32bits()
