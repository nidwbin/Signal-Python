import math

from matplotlib import pyplot
from signal.signals import Impulse, Step, RealFormulaSignal, PluralFormulaSignal
from signal.utils import Sampler, Recurrence
from signal.tools import draw


def formula1(n: int):
    """
    x(n) = e^((-0.2+0.7j)n)
    x(n) = e^(-0.2n)*e^(0.7nj)
    x(n) = e^(-0.2n)*(cos(0.7n)+j*sin(0.7n))
    x(n) = e^(-0.2n)*cos(0.7n)+j*e^(-0.2n)*sin(0.7n)
    """
    exp = math.exp(-0.2 * n)
    return exp * math.cos(0.7 * n), exp * math.sin(0.7 * n)


def formula2(n: int):
    n = n % 1
    return n * 2 - 1


if __name__ == '__main__':
    step = Step(-10, 10, 2, delta_time=0.01, signal_type=float)
    # start_time = -10
    # end_time = 10
    # impulse = Impulse(start_time, end_time)
    # step = Step(start_time, end_time)
    # signal1 = RealFormulaSignal(lambda x: 0.75 ** x, start_time, end_time)
    # signal2 = PluralFormulaSignal(formula1, start_time, end_time)
    # draw([impulse, step, signal1, signal2])
    # signal3 = RealFormulaSignal(formula2, 0, 2, delta_time=0.01, signal_type=float)
    # sample3 = Sampler(signal3, 32)
    # t1, x1 = zip(*list(signal3))
    # t2, x2 = zip(*list(sample3))
    # pyplot.plot(t1, x1)
    # pyplot.stem(t2, x2)
    # pyplot.xlabel("时间")
    # pyplot.ylabel("信号强度")
    # pyplot.show()
    #
    # rec1 = Recurrence([1, 0.75, 0.125], [1, -1], impulse)
    # rec2 = Recurrence([1, 0.75, 0.125], [1, -1], step)
    #
    # rec3 = Recurrence([1, -0.8], [0.15],
    #                   RealFormulaSignal(lambda x: 2 * math.sin(0.05 * math.pi * x),
    #                                     start_time, end_time)
    #                   )
    # signal4 = Step(-20, 20) - Step(-20, 20, switch_time=10)
    # rec4 = Recurrence([1, -0.9], [1], signal4)
    # draw([rec1, rec2, rec3, signal4, rec4])
