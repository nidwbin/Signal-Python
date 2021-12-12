import math

from .base import Signal, RealSignal, PluralSignal, MultiPluralSignal


class Sampler(RealSignal):
    # 连续信号采样器

    def __init__(self, signal: RealSignal, sample_num: int, *args, **kwargs):
        """
        :param signal: 信号
        :param sample_num: 采样数
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        """
        assert signal.signal_type is float
        start = signal.start
        end = signal.end
        rate = (sample_num - 1) / (start - end)
        self.signal = signal
        super(Sampler, self).__init__(*args, start=start, end=end, rate=rate, **kwargs)

    def __kernel__(self, var: float or int) -> float:
        return self.signal[var]


class Recurrence(RealSignal):
    def __init__(self, response_params: list, input_params: list, input_signal: RealSignal, *args, **kwargs):
        """
        :param response_params: 响应的参数
        :param input_params: 输入的参数
        :param input_signal: 输入信号
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        """
        self.response_params = response_params
        self.input_signal = input_signal
        self.input_params = input_params
        super(Recurrence, self).__init__(*args, start=input_signal.start, end=input_signal.end,
                                         rate=input_signal.rate, **kwargs)

    def __kernel__(self, var: float or int) -> float:
        result = 0
        for i in range(len(self.input_params)):
            result += self.input_signal[var - i * self.input_signal.delta] * self.input_params[i]
        for i in range(1, len(self.response_params)):
            result -= self[var - i * self.delta] * self.response_params[i]
        return result


class RealToPlural(PluralSignal):
    """
    将实数信号转换为复数信号
    """

    def __init__(self, signal: RealSignal, **kwargs):
        """
        :param signal: 待变换的信号
        """
        self.signal = signal
        super(RealToPlural, self).__init__(start=signal.start, end=signal.end,
                                           rate=signal.rate, signal_type=signal.signal_type, **kwargs)

    def __kernel__(self, var: float or int) -> (float, float):
        return self.signal[var], 0


class FT(PluralSignal):
    def __init__(self, signal: Signal, direction: int = -1, length: int = None, *args, **kwargs):
        """
        傅立叶变换的实现，包含离散傅立叶变换和离散傅立叶逆变换
        :param signal: 输入离散信号，包含实信号、复信号、DFT后的频谱密度
        :param direction: 变换方向，-1为离散傅立叶变换，1为离散傅立叶逆变换
        :param length: 信号长度，即N
        :param kwargs: 其他基类参数
        """
        self.direction = direction
        if self.direction == -1:
            assert signal.signal_type is int
            self.signal = RealToPlural(signal) if isinstance(signal, RealSignal) else signal
        elif self.direction == 1:
            assert isinstance(signal, FT) or isinstance(signal, MultiPluralSignal)
            self.signal = signal
        else:
            raise ValueError("Error direction.")
        end = self.signal.end if length is None else length - 1
        self.length = len(signal) if length is None else length
        super(FT, self).__init__(start=0, end=end, *args, **kwargs)

    def __kernel__(self, var: float or int) -> (float, float):
        ret1 = ret2 = 0
        for i in range(self.length):
            x1, y1 = self.signal.get_nth(i)
            x2 = math.cos(self.direction * 2 * math.pi * i * var / self.length)
            y2 = math.sin(self.direction * 2 * math.pi * i * var / self.length)
            ret1 += x1 * x2 - y1 * y2
            ret2 += x1 * y2 + x2 * y1
        if self.direction == 1:
            ret1 /= self.length
            ret2 /= self.length
        return ret1, ret2


class DFT(FT):
    def __init__(self, signal: Signal, length: int = None, *args, **kwargs):
        super(DFT, self).__init__(signal, -1, length, *args, **kwargs)


class IDFT(FT):
    def __init__(self, signal: Signal, length: int = None, *args, **kwargs):
        super(IDFT, self).__init__(signal, 1, length, *args, **kwargs)


class DTFT(PluralSignal):
    """
    离散时间傅立叶变换
    """

    def __init__(self, signal: Signal, *args, **kwargs):
        assert signal.cycle is False and signal.signal_type is int
        self.signal = RealToPlural(signal) if isinstance(signal, RealSignal) else signal
        super(DTFT, self).__init__(*args, signal_type=float, **kwargs)

    def __kernel__(self, var: float or int) -> (float, float):
        ret1 = ret2 = 0
        for n, x1, y1 in self.signal:
            x2 = math.cos(-n * var)
            y2 = math.sin(-n * var)
            ret1 += x1 * x2 - y1 * y2
            ret2 += x1 * y2 + x2 * y1
        return ret1, ret2
