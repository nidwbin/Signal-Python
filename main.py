import math

from matplotlib import pyplot
from signal.signals import Impulse, Step, RealFormulaSignal, PluralFormulaSignal
from signal.utils import Sampler, Recurrence
from signal.tools import draw


def formula1(n: int or float):
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
    draw([Impulse(-10, 10, 2), Impulse(-10, 10, 2, delta_time=0.01, signal_type=float)])

    draw([Step(-10, 10, 2), Step(-10, 10, 2, delta_time=0.01, signal_type=float)])

    draw([RealFormulaSignal(lambda x: 0.75 ** x, -10, 10),
          RealFormulaSignal(lambda x: 0.75 ** x, -10, 10,delta_time=0.01, signal_type=float)])

    PluralFormulaSignal(formula1, -10, 10).draw()

    signal3 = RealFormulaSignal(formula2, 0, 2, delta_time=0.01, signal_type=float)
    sample3 = Sampler(signal3, 32)
    t1, x1 = zip(*list(signal3))
    t2, x2 = zip(*list(sample3))
    pyplot.plot(t1, x1)
    pyplot.stem(t2, x2)
    pyplot.xlabel("时间")
    pyplot.ylabel("信号强度")
    pyplot.show()

    impulse = Impulse(-20, 20)
    rec1 = Recurrence([1, 0.75, 0.125], [1, -1], impulse)
    rec1.draw()

    step = Step(-20, 20)
    rec2 = Recurrence([1, 0.75, 0.125], [1, -1], step)
    rec2.draw()

    rec3 = Recurrence([1, -0.8], [0.15],
                      RealFormulaSignal(lambda x: 2 * math.sin(0.05 * math.pi * x), -20, 20))
    rec3.draw()

    signal4 = Step(-20, 20) - Step(-20, 20, switch_time=10)
    signal4.draw()
    rec4 = Recurrence([1, -0.9], [1], signal4)
    rec4.draw()
