import abc
from abc import ABC

from matplotlib import pyplot
from matplotlib.pyplot import MultipleLocator

pyplot.rcParams['font.sans-serif'] = ['SimHei']
pyplot.rcParams['axes.unicode_minus'] = False


class Signal(metaclass=abc.ABCMeta):
    """
    信号基类
    """

    def __init__(self, start_time: float or int = 0, end_time: float or int = 0,
                 delta_time: float or int = 1, signal_type=int):
        """
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param delta_time: 最小时间片
        :param signal_type: 信号类型
        """
        assert signal_type in [int, float]
        self.signal_type = signal_type
        self.delta_time = delta_time

        assert start_time <= end_time
        self.start_time = start_time
        self.end_time = end_time

    def __iter__(self):
        raise NotImplementedError

    def __getitem__(self, time: float or int):
        if time < self.start_time or time > self.end_time:
            return 0
        else:
            return self.__kernel__(time)

    def __kernel__(self, time: float or int):
        """
        信号实际函数
        获取time时刻的信号状态
        :param time: 时刻
        :return: 信号状态
        """
        raise NotImplementedError

    def __stem__(self, t: list, x: list, x_label: str, t_label: str = "时间"):
        if self.delta_time / (self.end_time - self.start_time) >= 0.05:
            pyplot.gca().xaxis.set_major_locator(MultipleLocator(self.delta_time))
        pyplot.stem(t, x)
        pyplot.xlabel(t_label)
        pyplot.ylabel(x_label)
        pyplot.show()

    @staticmethod
    def __plot__(t: list, x: list, x_label: str, t_label: str = "时间"):
        pyplot.plot(t, x)
        pyplot.xlabel(t_label)
        pyplot.ylabel(x_label)
        pyplot.show()


class RealSignal(Signal, metaclass=abc.ABCMeta):
    """
    实数信号基类
    """

    def __add__(self, other):
        assert issubclass(type(other), RealSignal)
        return MultiRealSignal(self, other, "+")

    def __sub__(self, other):
        assert issubclass(type(other), RealSignal)
        return MultiRealSignal(self, other, "-")

    def __mul__(self, other):
        assert issubclass(type(other), RealSignal)
        return MultiRealSignal(self, other, "*")

    def __iter__(self) -> (float or int, float):
        """
        实数信号默认迭代器，产生从start time到end time以delta time为时间间隔的序列
        :return: (时间，信号强度）
        """
        now = self.start_time
        while now <= self.end_time:
            yield now, self[now]
            now += self.delta_time

    def draw(self):
        t, y = zip(*list(self))
        if self.signal_type is int:
            self.__stem__(t, y, "信号强度")
        else:
            self.__plot__(t, y, "信号强度")


class MultiRealSignal(RealSignal, metaclass=abc.ABCMeta):
    """
    复合实数信号基类
    """

    def __init__(self, signal1: RealSignal, signal2: RealSignal, multi_type: str, *args, **kwargs):
        assert signal1.delta_time == signal1.delta_time and signal2.signal_type == signal2.signal_type
        self.signal1 = signal1
        self.signal2 = signal2
        assert multi_type in ["+", "-", "*"]
        self.multi_type = multi_type
        super(MultiRealSignal, self).__init__(*args, start_time=min(signal1.start_time, signal2.start_time),
                                              end_time=max(signal1.end_time, signal2.end_time),
                                              delta_time=signal1.delta_time, **kwargs)

    def __getitem__(self, time: float or int) -> float:
        if time < self.start_time or time > self.end_time:
            return 0
        elif self.multi_type == '+':
            return self.signal1[time] + self.signal2[time]
        elif self.multi_type == '-':
            return self.signal1[time] - self.signal2[time]
        elif self.multi_type == '*':
            return self.signal1[time] * self.signal2[time]


class PluralSignal(Signal, metaclass=abc.ABCMeta):
    """
    复数信号基类
    """

    def __add__(self, other):
        assert issubclass(type(other), PluralSignal)
        return MultiPluralSignal(self, other, "+")

    def __sub__(self, other):
        assert issubclass(type(other), PluralSignal)
        return MultiPluralSignal(self, other, "-")

    def __mul__(self, other):
        assert issubclass(type(other), PluralSignal)
        return MultiPluralSignal(self, other, "*")

    def __iter__(self) -> (float or int, float, float):
        """
        复数信号默认迭代器，产生从start time到end time以delta time为时间间隔的序列
        :return: (时间，实部信号强度，复部信号强度）
        """
        now = self.start_time
        while now <= self.end_time:
            x, y = self[now]
            yield now, x, y
            now += self.delta_time

    @staticmethod
    def __plot_3d__(t: list, x: list, y: list, x_label: str, y_label: str, t_label: str = "时间"):
        ax = pyplot.axes(projection="3d")
        ax.scatter3D(t, x, y)
        ax.plot3D(t, x, y)
        ax.set_xlabel(t_label)
        ax.set_ylabel(x_label)
        ax.set_zlabel(y_label)
        pyplot.show()

    def draw(self):
        t, x, y = zip(*list(self))
        self.__plot_3d__(t, x, y, "实部信号强度", "虚部信号强度")
        if self.signal_type is int:
            self.__stem__(t, x, "实部信号强度")
            self.__stem__(t, y, "虚部信号强度")
            pyplot.scatter(x, y)
        else:
            self.__plot__(t, x, "实部信号强度")
            self.__plot__(t, y, "虚部信号强度")
        self.__plot__(x, y, "虚部信号强度", "实部信号强度")


class MultiPluralSignal(RealSignal, metaclass=abc.ABCMeta):
    """
    复合复数信号基类
    """

    def __init__(self, signal1: PluralSignal, signal2: PluralSignal, multi_type: str, *args, **kwargs):
        assert signal1.delta_time == signal1.delta_time and signal2.signal_type == signal2.signal_type
        self.signal1 = signal1
        self.signal2 = signal2
        assert multi_type in ["+", "-", "*"]
        self.multi_type = multi_type
        super(MultiPluralSignal, self).__init__(*args, start_time=min(signal1.start_time, signal2.start_time),
                                                end_time=max(signal1.end_time, signal2.end_time),
                                                delta_time=signal1.delta_time, **kwargs)

    def __getitem__(self, time: float or int) -> (float, float):
        x1, y1 = self.signal1[time]
        x2, y2 = self.signal2[time]
        if time < self.start_time or time > self.end_time:
            return 0, 0
        elif self.multi_type == '+':
            return x1 + x2, y1 + y2
        elif self.multi_type == '-':
            return x1 - x2, y1 - y2
        elif self.multi_type == '*':
            return x1 * x2 - y1 * y2, x1 * y2 + x2 * y1
