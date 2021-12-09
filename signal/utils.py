import math

from .signals import PluralFormulaSignal
from .base import Signal, RealSignal, PluralSignal


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
        :param signal:
        """
        self.signal = signal
        super(RealToPlural, self).__init__(start=signal.start, end=signal.end,
                                           rate=signal.rate, signal_type=signal.signal_type, **kwargs)

    def __kernel__(self, var: float or int) -> (float, float):
        return self.signal[var], 0
