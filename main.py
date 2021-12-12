import os
import math
import numpy
from signal.signals import RealSeqSignal
from signal.utils import DFT, IDFT, DTFT


def formula(M):
    xa = numpy.arange(0, math.floor(M / 2) + 1)
    xb = numpy.arange(math.ceil(M / 2) - 1, -1, -1)
    x = numpy.concatenate((xa, xb))
    return x


if __name__ == '__main__':
    for N in [8, 16, 32, 64]:
        R_5 = RealSeqSignal([1 for i in range(5)], start=0, end=4)
        dft = DFT(R_5, length=N)
        dir_name = f'./1_{N}'
        os.mkdir(dir_name)
        dft.update(t_label=r"$k$", x_label=r"$Re(X(k))$", y_label=r"$Im(X(k))$", save=True, save_dir=dir_name)
        dft.draw()
    M = 27
    x = RealSeqSignal(formula(M), 0, M)

    dtft = DTFT(x, -10, 10, rate=100)
    dir_name = f'./2_dtft'
    os.mkdir(dir_name)
    dtft.update(t_label=r"$\omega$", x_label=r"$Re(X(e^{j\omega}))$", y_label=r"$Im(X(e^{j\omega}))$", save=True,
                save_dir=dir_name)
    dtft.draw()

    for N in [8, 16, 32, 64, 128]:
        dft = DFT(x, length=N)
        dir_name = f'./2_{N}'
        os.mkdir(dir_name)
        dft.update(t_label=r"$k$", x_label=r"$Re(X(k))$", y_label=r"$Im(X(k))$", save=True, save_dir=dir_name)
        dft.draw()
    for N in [8, 16, 32, 64, 128]:
        dft = DFT(x, length=N)
        idft = IDFT(dft, length=N)
        dir_name = f'./2_{N}_'
        os.mkdir(dir_name)
        idft.update(t_label=r"$n$", x_label=r"$Re(x(n))$", y_label=r"$Im(x(n))$", save=True, save_dir=dir_name)
        idft.draw()

    x = [2, 3, 1, 4, 5]
    h = [2, 1, 7, 4, 5, 7, 2, 3]
    dir_name = f'./3_1'
    os.mkdir(dir_name)
    x_ = RealSeqSignal(x, start=0, end=len(x) - 1)
    h_ = RealSeqSignal(h, start=0, end=len(h) - 1)
    n = len(x) + len(h) - 1
    d1 = DFT(x_, length=n)
    d2 = DFT(h_, length=n)
    y = IDFT(d1 * d2)
    y.update(t_label=r"$n$", x_label=r"$Re(x(n))$", y_label=r"$Im(x(n))$", save=True, save_dir=dir_name)
    y.draw()

    dir_name = f'./3_2'
    os.mkdir(dir_name)
    cov = (x_ ** h_)
    cov.update(t_label=r"$n$", x_label=r"$x(n)$", save=True, save_dir=dir_name)
    cov.draw()
