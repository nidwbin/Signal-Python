import abc
import math

from matplotlib import pyplot
from matplotlib.pyplot import MultipleLocator

pyplot.rcParams['font.sans-serif'] = ['SimHei']
pyplot.rcParams['axes.unicode_minus'] = False


class Drawable(metaclass=abc.ABCMeta):
    def draw(self):
        raise NotImplementedError


class Signal(Drawable, metaclass=abc.ABCMeta):
    # 信号基类

    def __init__(self, start_time: float or int = 0, end_time: float or int = 0, rate: float or int = 1,
                 signal_type=int, zero_hold: bool = False, deviation: float = 1e-10, cache: bool = True):
        """
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param rate: 对于连续信号为绘制频率，只在迭代器上生效，对于离散信号为采样率，要求计算过程中采样率对齐
        :param signal_type: 信号类型
        :param zero_hold: 0阶保持器
        :param deviation: 浮点数计算误差
        :param cache: 是否缓存结果
        """
        self.zero_hold = zero_hold
        self.deviation = deviation
        assert signal_type in [int, float]
        self.signal_type = signal_type
        assert rate > 0
        self.delta_time = 1 / rate
        self.rate = rate

        assert start_time <= end_time
        self.start_time = start_time
        self.end_time = end_time
        self.cache = cache
        self.cache_list = []
        self.time_list = []

    def __iter__(self):
        raise NotImplementedError

    def __getitem__(self, time: float or int):
        if time < self.start_time or time > self.end_time:
            return 0
        else:
            if self.signal_type is int:
                # 离散信号，采样率对齐，若未使用0阶保持器，采样点外一律为0
                mul = round((time - self.start_time) / self.delta_time)
                if self.zero_hold or math.isclose(time, self.start_time + self.delta_time * mul,
                                                  abs_tol=self.deviation):
                    # 使用0阶保持器或在浮点数计算误差范围之内
                    time = self.start_time + self.delta_time * mul
                else:
                    return 0
            if self.cache:
                if time in self.time_list:
                    ret = self.cache_list[self.time_list.index(time)]
                else:
                    ret = self.__kernel__(time)
                    self.cache_list.append(ret)
                    self.time_list.append(time)
            else:
                ret = self.__kernel__(time)
            return ret

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

    def solve(self):
        return zip(*list(self))

    def update(self, start_time: float or int = None, end_time: float or int = None, rate: float or int = None,
               signal_type=None, zero_hold: bool = None, deviation: float = None, cache: bool = None):
        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time
        assert self.start_time <= self.end_time
        if rate is not None:
            assert signal_type in [int, float]
            self.delta_time = 1 / rate
            self.rate = rate
        if signal_type is not None:
            assert signal_type in [int, float]
            self.signal_type = signal_type
        if zero_hold is not None:
            self.zero_hold = zero_hold
        if deviation is not None:
            self.deviation = deviation
        if cache is not None:
            self.cache = cache

    @staticmethod
    def __plot__(t: list, x: list, x_label: str, t_label: str = "时间"):
        pyplot.plot(t, x)
        pyplot.xlabel(t_label)
        pyplot.ylabel(x_label)
        pyplot.show()


class RealSignal(Signal, metaclass=abc.ABCMeta):
    # 实数信号基类
    def __init__(self, *args, t_label="时间", x_label="信号强度", **kwargs):
        self.t_label = t_label
        self.x_label = x_label
        super(RealSignal, self).__init__(*args, **kwargs)

    def __add__(self, other):
        assert issubclass(type(other), RealSignal)
        return MultiRealSignal(self, other, "+")

    def __sub__(self, other):
        assert issubclass(type(other), RealSignal)
        return MultiRealSignal(self, other, "-")

    def __mul__(self, other):
        assert issubclass(type(other), RealSignal)
        return MultiRealSignal(self, other, "*")

    def __pow__(self, other):
        # 卷积运算
        assert issubclass(type(other), RealSignal)
        return MultiRealSignal(self, other, "**")

    def __iter__(self) -> (float or int, float):
        """
        实数信号默认迭代器，产生从start time到end time以delta time为时间间隔的序列
        :return: (时间，信号强度）
        """
        cnt = 0
        now = self.start_time
        while now <= self.end_time:
            yield now, self[now]
            cnt += 1
            now = self.start_time + self.delta_time * cnt

    def update(self, t_label=None, x_label=None, **kwargs):
        if t_label is not None:
            self.t_label = t_label
        if x_label is not None:
            self.x_label = x_label
        super(RealSignal, self).update(**kwargs)

    def draw(self):
        t, y = self.solve()
        if self.signal_type is int:
            self.__stem__(t, y, x_label=self.x_label, t_label=self.t_label)
        else:
            self.__plot__(t, y, x_label=self.x_label, t_label=self.t_label)


class PluralSignal(Signal, metaclass=abc.ABCMeta):
    # 复数信号基类
    def __init__(self, *args, t_label="时间", x_label="实部信号强度", y_label="虚部信号强度", **kwargs):
        self.t_label = t_label
        self.x_label = x_label
        self.y_label = y_label
        super(PluralSignal, self).__init__(*args, **kwargs)

    def __add__(self, other):
        assert issubclass(type(other), PluralSignal)
        return MultiPluralSignal(self, other, "+")

    def __sub__(self, other):
        assert issubclass(type(other), PluralSignal)
        return MultiPluralSignal(self, other, "-")

    def __mul__(self, other):
        assert issubclass(type(other), PluralSignal)
        return MultiPluralSignal(self, other, "*")

    def __pow__(self, other):
        # 卷积运算
        assert issubclass(type(other), PluralSignal)
        return MultiPluralSignal(self, other, "**")

    def __iter__(self) -> (float or int, float, float):
        """
        复数信号默认迭代器，产生从start time到end time以delta time为时间间隔的序列
        :return: (时间，实部信号强度，复部信号强度）
        """
        cnt = 0
        now = self.start_time
        while now <= self.end_time:
            x, y = self[now]
            yield now, x, y
            cnt += 1
            now = self.start_time + self.delta_time * cnt

    @staticmethod
    def __plot_3d__(t: list, x: list, y: list, x_label: str, y_label: str, t_label: str = "时间"):
        ax = pyplot.axes(projection="3d")
        ax.scatter3D(t, x, y)
        ax.plot3D(t, x, y)
        ax.set_xlabel(t_label)
        ax.set_ylabel(x_label)
        ax.set_zlabel(y_label)
        pyplot.show()

    def update(self, t_label=None, x_label=None, y_label=None, **kwargs):
        if t_label is not None:
            self.t_label = t_label
        if x_label is not None:
            self.x_label = x_label
        if y_label is not None:
            self.y_label = y_label
        super(PluralSignal, self).update(**kwargs)

    def draw(self):
        t, x, y = self.solve()
        self.__plot_3d__(t, x, y, self.x_label, self.y_label, self.t_label)
        if self.signal_type is int:
            self.__stem__(t, x, self.x_label, self.t_label)
            self.__stem__(t, y, self.y_label, self.t_label)
            pyplot.scatter(x, y)
        else:
            self.__plot__(t, x, self.x_label, self.t_label)
            self.__plot__(t, y, self.y_label, self.t_label)
        self.__plot__(x, y, self.y_label, self.x_label)


class MultiRealSignal(RealSignal, metaclass=abc.ABCMeta):
    # 复合实数信号基类

    def __init__(self, signal1: RealSignal, signal2: RealSignal, multi_type: str, *args, **kwargs):
        signal_type = int
        if signal1.signal_type is int and signal2.signal_type is int:
            assert signal1.delta_time == signal2.delta_time
            rate = signal1.rate
        elif signal1.signal_type is int:
            rate = signal1.rate
        else:
            if signal2.signal_type is float:
                signal_type = float
            rate = signal2.rate
        self.signal1 = signal1
        self.signal2 = signal2
        assert multi_type in ["+", "-", "*", "**"]
        self.multi_type = multi_type
        super(MultiRealSignal, self).__init__(*args, start_time=min(signal1.start_time, signal2.start_time),
                                              end_time=max(signal1.end_time, signal2.end_time),
                                              rate=rate, signal_type=signal_type, **kwargs)

    def __getitem__(self, time: float or int) -> float:
        if time < self.start_time or time > self.end_time:
            return 0
        if self.cache and time in self.time_list:
            return self.cache_list[self.time_list.index(time)]
        ret = 0
        if self.multi_type == '+':
            ret = self.signal1[time] + self.signal2[time]
        elif self.multi_type == '-':
            ret = self.signal1[time] - self.signal2[time]
        elif self.multi_type == '*':
            ret = self.signal1[time] * self.signal2[time]
        elif self.multi_type == '**':
            cnt = 0
            delt = self.start_time
            while delt <= self.end_time:
                ret += self.signal1[delt] * self.signal2[time - delt]
                cnt += 1
                delt = self.start_time + self.delta_time * cnt
        if self.cache:
            self.time_list.append(time)
            self.cache_list.append(ret)
        return ret


class MultiPluralSignal(RealSignal, metaclass=abc.ABCMeta):
    # 复合复数信号基类

    def __init__(self, signal1: PluralSignal, signal2: PluralSignal, multi_type: str, *args, **kwargs):
        signal_type = int
        if signal1.signal_type is int and signal2.signal_type is int:
            assert signal1.delta_time == signal2.delta_time
            rate = signal1.rate
        elif signal1.signal_type is int:
            rate = signal1.rate
        else:
            if signal2.signal_type is float:
                signal_type = float
            rate = signal2.rate
        self.signal1 = signal1
        self.signal2 = signal2
        assert multi_type in ["+", "-", "*", "**"]
        self.multi_type = multi_type
        super(MultiPluralSignal, self).__init__(*args, start_time=min(signal1.start_time, signal2.start_time),
                                                end_time=max(signal1.end_time, signal2.end_time),
                                                rate=rate, signal_type=signal_type, **kwargs)

    def __getitem__(self, time: float or int) -> (float, float):
        if time < self.start_time or time > self.end_time:
            return 0, 0
        if self.cache and time in self.time_list:
            return self.cache_list[self.time_list.index(time)]
        x1, y1 = self.signal1[time]
        x2, y2 = self.signal2[time]
        ret1 = 0
        ret2 = 0
        if self.multi_type == '+':
            ret1 = x1 + x2
            ret2 = y1 + y2
        elif self.multi_type == '-':
            ret1 = x1 - x2
            ret2 = y1 - y2
        elif self.multi_type == '*':
            ret1 = x1 * x2 - y1 * y2
            ret2 = x1 * y2 + x2 * y1
        elif self.multi_type == '**':
            cnt = 0
            delt = self.start_time
            while delt <= self.end_time:
                x1, y1 = self.signal1[delt]
                x2, y2 = self.signal2[time - delt]
                ret1 += x1 * x2 - y1 * y2
                ret2 += x1 * y2 + x2 * y1
                cnt += 1
                delt = self.start_time + self.delta_time * cnt
        if self.cache:
            self.time_list.append(time)
            self.cache_list.append((ret1, ret2))
        return ret1, ret2
