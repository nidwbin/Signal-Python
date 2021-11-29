from .base import RealSignal


class Sample(RealSignal):
    """
    连续信号采样器
    """

    def __init__(self, signal: RealSignal, sample_num: int, *args, **kwargs):
        """
        :param signal: 信号
        :param sample_num: 采样数
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        """
        assert signal.signal_type is float
        start_time = signal.start_time
        end_time = signal.end_time
        delta_time = (end_time - start_time) / (sample_num - 1)
        self.signal = signal
        super(Sample, self).__init__(*args, start_time=start_time, end_time=end_time, delta_time=delta_time, **kwargs)

    def __kernel__(self, time: float or int) -> float:
        return self.signal[time]


class Recurrence(RealSignal):
    def __init__(self, response_params: list, input_params: list, input_signal: RealSignal, *args, **kwargs):
        """
        :param response_params: 响应的参数
        :param input_params: 输入的参数
        :param input_signal: 输入信号
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        cache: 求解结果缓存
        times: 求解过的时间
        """
        self.cache = []
        self.times = []
        self.response_params = response_params
        self.input_signal = input_signal
        self.input_params = input_params
        super(Recurrence, self).__init__(*args, start_time=input_signal.start_time, end_time=input_signal.end_time,
                                         delta_time=input_signal.delta_time, **kwargs)

    def __kernel__(self, time: float or int) -> float:
        if time in self.times:
            return self.cache[self.times.index(time)]
        else:
            result = 0
            for i in range(len(self.input_params)):
                result += self.input_signal[time - i * self.input_signal.delta_time] * self.input_params[i]
            for i in range(1, len(self.response_params)):
                result -= self[time - i * self.delta_time] * self.response_params[i]
            self.times.append(time)
            self.cache.append(result / self.response_params[0])
            return self.cache[-1]
