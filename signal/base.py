import abc
import math
import os

from matplotlib import pyplot
from matplotlib.pyplot import MultipleLocator

pyplot.rcParams['font.sans-serif'] = ['SimHei']
pyplot.rcParams['axes.unicode_minus'] = False


class Drawable(metaclass=abc.ABCMeta):
    def draw(self):
        raise NotImplementedError


class Signal(Drawable, metaclass=abc.ABCMeta):
    # 信号基类

    def __init__(self, start: float or int = 0, end: float or int = 0, rate: float or int = 1,
                 signal_type=int, cycle: bool = False, zero_hold: bool = False, deviation: float = 1e-10,
                 cache: bool = True, save: bool = False, save_dir: str = './'):
        """
        :param start: 开始时间
        :param end: 结束时间
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

        self.cycle = cycle

        assert rate > 0
        self.delta = 1 / rate
        self.rate = rate

        assert start <= end
        self.start = start
        self.end = end
        self.cache = cache
        self.cache_list = []
        self.var_list = []

        self.save = save
        if self.save:
            assert os.path.exists(save_dir)
        self.save_dir = save_dir

    def __len__(self) -> int:
        return math.floor((self.end - self.start) / self.delta) + 1

    def __iter__(self):
        raise NotImplementedError

    def __getitem__(self, var: float or int):
        if self.cycle:
            var = (var - self.start) % (self.end - self.start + self.delta) + self.start

        if self.signal_type is int:
            # 离散信号，采样率对齐，若未使用0阶保持器，采样点外一律为0
            mul = round((var - self.start) / self.delta)
            if self.zero_hold or math.isclose(var, self.start + self.delta * mul,
                                              abs_tol=self.deviation):
                # 使用0阶保持器或在浮点数计算误差范围之内
                var = self.start + self.delta * mul
            else:
                return 0
        if self.cache:
            if var in self.var_list:
                ret = self.cache_list[self.var_list.index(var)]
            else:
                ret = self.__kernel__(var)
                self.cache_list.append(ret)
                self.var_list.append(var)
        else:
            ret = self.__kernel__(var)
        return ret

    def get_nth(self, n: int):
        return self[self.start + self.delta * n]

    def __kernel__(self, var: float or int):
        """
        信号实际函数
        获取输入var时的信号状态
        :param var: 时刻
        :return: 信号状态
        """
        raise NotImplementedError

    def __stem__(self, t: list, x: list, x_label: str, t_label: str = "时间", save_name: str = '1.png'):
        if self.delta / (self.end - self.start) >= 0.05:
            pyplot.gca().xaxis.set_major_locator(MultipleLocator(self.delta))
        pyplot.stem(t, x)
        pyplot.xlabel(t_label)
        pyplot.ylabel(x_label)
        if self.save:
            pyplot.savefig(os.path.join(self.save_dir, save_name), bbox_inches='tight')
        pyplot.show()

    def solve(self):
        return zip(*list(self))

    def clear(self):
        self.cache_list.clear()
        self.var_list.clear()

    def update(self, start: float or int = None, end: float or int = None, rate: float or int = None,
               signal_type=None, cycle=None, zero_hold: bool = None, deviation: float = None, cache: bool = None,
               save=None, save_dir=None):
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end
        assert self.start <= self.end
        if rate is not None:
            assert signal_type in [int, float]
            self.delta = 1 / rate
            self.rate = rate
        if signal_type is not None:
            assert signal_type in [int, float]
            self.signal_type = signal_type
        if cycle is not None:
            self.cycle = cycle
        if zero_hold is not None:
            self.zero_hold = zero_hold
        if deviation is not None:
            self.deviation = deviation
        if cache is not None:
            self.cache = cache
        if save is not None:
            self.save = save
        if save_dir is not None:
            if self.save:
                assert os.path.exists(save_dir)
            self.save_dir = save_dir

    def __plot__(self, t: list, x: list, x_label: str, t_label: str = "时间", save_name: str = '1.png'):
        pyplot.plot(t, x)
        pyplot.xlabel(t_label)
        pyplot.ylabel(x_label)
        if self.save:
            pyplot.savefig(os.path.join(self.save_dir, save_name), bbox_inches='tight')
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
        实数信号默认迭代器，产生从start到end以delta为间隔的序列
        :return: (时间，信号强度）
        """
        cnt = 0
        now = self.start
        while now <= self.end:
            yield now, self[now]
            cnt += 1
            now = self.start + self.delta * cnt

    def __getitem__(self, var: float or int) -> float:
        if not self.cycle and var < self.start or var > self.end:
            return 0
        ret = super(RealSignal, self).__getitem__(var)
        ret = 0 if math.isclose(ret, 0, abs_tol=self.deviation) else ret
        return ret

    def update(self, t_label=None, x_label=None, **kwargs):
        if t_label is not None:
            self.t_label = t_label
        if x_label is not None:
            self.x_label = x_label
        super(RealSignal, self).update(**kwargs)

    def draw(self):
        t, y = self.solve()
        if self.signal_type is int:
            self.__stem__(t, y, x_label=self.x_label, t_label=self.t_label, save_name='1.png')
        else:
            self.__plot__(t, y, x_label=self.x_label, t_label=self.t_label, save_name='1.png')


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
        复数信号默认迭代器，产生从start到end以delta为间隔的序列
        :return: (时间，实部信号强度，复部信号强度）
        """
        cnt = 0
        now = self.start
        while now <= self.end:
            x, y = self[now]
            yield now, x, y
            cnt += 1
            now = self.start + self.delta * cnt

    def __getitem__(self, var: float or int) -> (float, float):
        if not self.cycle and var < self.start or var > self.end:
            return 0, 0
        ret1, ret2 = super(PluralSignal, self).__getitem__(var)
        ret1 = 0 if math.isclose(ret1, 0, abs_tol=self.deviation) else ret1
        ret2 = 0 if math.isclose(ret2, 0, abs_tol=self.deviation) else ret2
        return ret1, ret2

    def __plot_3d__(self, t: list, x: list, y: list, x_label: str, y_label: str, t_label: str = "时间",
                    save_name: str = '1.png'):
        ax = pyplot.axes(projection="3d")
        ax.scatter3D(t, x, y)
        ax.plot3D(t, x, y)
        ax.set_xlabel(t_label)
        ax.set_ylabel(x_label)
        ax.set_zlabel(y_label)
        if self.save:
            pyplot.savefig(os.path.join(self.save_dir, save_name), bbox_inches='tight')
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
        self.__plot_3d__(t, x, y, self.x_label, self.y_label, self.t_label, '1.png')
        if self.signal_type is int:
            self.__stem__(t, x, self.x_label, self.t_label, '2.png')
            self.__stem__(t, y, self.y_label, self.t_label, '3.png')
            pyplot.scatter(x, y)
        else:
            self.__plot__(t, x, self.x_label, self.t_label, '2.png')
            self.__plot__(t, y, self.y_label, self.t_label, '3.png')
        self.__plot__(x, y, self.y_label, self.x_label, '4.png')


class MultiRealSignal(RealSignal, metaclass=abc.ABCMeta):
    # 复合实数信号基类

    def __init__(self, signal1: RealSignal, signal2: RealSignal, multi_type: str, *args, **kwargs):
        signal_type = int
        if signal1.signal_type is int and signal2.signal_type is int:
            assert signal1.delta == signal2.delta
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
        end = len(signal1) + len(signal2) - 2 if multi_type == "**" else max(signal1.end, signal2.end)
        super(MultiRealSignal, self).__init__(*args, start=min(signal1.start, signal2.start), end=end,
                                              rate=rate, signal_type=signal_type, **kwargs)

    def __getitem__(self, var: float or int) -> float:
        if var < self.start or var > self.end:
            return 0
        if self.cache and var in self.var_list:
            return self.cache_list[self.var_list.index(var)]
        ret = 0
        if self.multi_type == '+':
            ret = self.signal1[var] + self.signal2[var]
        elif self.multi_type == '-':
            ret = self.signal1[var] - self.signal2[var]
        elif self.multi_type == '*':
            ret = self.signal1[var] * self.signal2[var]
        elif self.multi_type == '**':
            cnt = 0
            delt = self.start
            while delt <= self.end:
                ret += self.signal1[delt] * self.signal2[var - delt]
                cnt += 1
                delt = self.start + self.delta * cnt
        ret = 0 if math.isclose(ret, 0, abs_tol=self.deviation) else ret
        if self.cache:
            self.var_list.append(var)
            self.cache_list.append(ret)
        return ret


class MultiPluralSignal(PluralSignal, metaclass=abc.ABCMeta):
    # 复合复数信号基类

    def __init__(self, signal1: PluralSignal, signal2: PluralSignal, multi_type: str, *args, **kwargs):
        signal_type = int
        if signal1.signal_type is int and signal2.signal_type is int:
            assert signal1.delta == signal2.delta
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
        end = len(signal1) + len(signal2) - 2 if multi_type == "**" else max(signal1.end, signal2.end)
        super(MultiPluralSignal, self).__init__(*args, start=min(signal1.start, signal2.start), end=end,
                                                rate=rate, signal_type=signal_type, **kwargs)

    def __getitem__(self, var: float or int) -> (float, float):
        if var < self.start or var > self.end:
            return 0.0, 0.0
        if self.cache and var in self.var_list:
            return self.cache_list[self.var_list.index(var)]
        x1, y1 = self.signal1[var]
        x2, y2 = self.signal2[var]
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
            delt = self.start
            while delt <= self.end:
                x1, y1 = self.signal1[delt]
                x2, y2 = self.signal2[var - delt]
                ret1 += x1 * x2 - y1 * y2
                ret2 += x1 * y2 + x2 * y1
                cnt += 1
                delt = self.start + self.delta * cnt
        ret1 = 0 if math.isclose(ret1, 0, abs_tol=self.deviation) else ret1
        ret2 = 0 if math.isclose(ret2, 0, abs_tol=self.deviation) else ret2
        if self.cache:
            self.var_list.append(var)
            self.cache_list.append((ret1, ret2))
        return ret1, ret2
