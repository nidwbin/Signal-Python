import math
from collections.abc import Callable
from .base import RealSignal, PluralSignal


class Impulse(RealSignal):
    """
    实数冲激信号
    """

    def __init__(self, start: float or int = 0, end: float or int = 0,
                 switch: float or int = None, strength: float = 1, *args, **kwargs):
        """
        :param start: 开始时间
        :param end: 停止时间
        :param switch: 信号状态切换时间
        :param strength: 强度
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        """
        super(Impulse, self).__init__(start, end, *args, **kwargs)
        self.strength = strength
        if switch is None:
            # 默认值，选开始和结束时间的中点
            if self.signal_type is int:
                self.switch = (self.start + self.end) // 2
            else:
                self.switch = (self.start + self.end) / 2
        else:
            assert self.start <= switch <= self.end
            self.switch = switch
        # 冲激时间与最小间隔对齐
        self.switch = (self.switch - self.start) // self.delta
        self.switch = self.switch * self.delta + self.start

    def __kernel__(self, var: float or int) -> float:
        return self.strength if var == self.switch else 0


class Step(RealSignal):
    """
    实数阶跃信号
    """

    def __init__(self, start: float or int = 0, end: float or int = 0,
                 switch: float or int = None, strength: float = 1, *args, **kwargs):
        """
        :param start: 开始时间
        :param end: 停止时间
        :param switch: 信号状态切换时间
        :param strength: 强度
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        """
        super(Step, self).__init__(start, end, *args, **kwargs)
        self.strength = strength
        if switch is None:
            # 默认值，选开始和结束时间的中点
            if self.signal_type is int:
                self.switch = (self.start + self.end) // 2
            else:
                self.switch = (self.start + self.end) / 2
        else:
            assert self.start <= switch <= self.end
            self.switch = switch
        # 阶跃时间与最小时间片对齐
        self.switch = (self.switch - self.start) // self.delta
        self.switch = self.switch * self.delta + self.start

    def __kernel__(self, var: float or int) -> float:
        return self.strength if var >= self.switch else 0.0


class RealFormulaSignal(RealSignal):
    """
    使用实数公式或函数构建信号
    """

    def __init__(self, formula: Callable[float or int], *args, **kwargs):
        """
        :param formula: 公式或函数
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        """
        self.formula = formula
        super(RealFormulaSignal, self).__init__(*args, **kwargs)

    def __kernel__(self, var: float or int) -> float:
        return self.formula(var)


class PluralFormulaSignal(PluralSignal):
    # 使用复数公式或函数构建信号

    def __init__(self, formula: Callable[float or int], *args, **kwargs):
        """
        :param formula: 公式或函数
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        """
        self.formula = formula
        super(PluralFormulaSignal, self).__init__(*args, **kwargs)

    def __kernel__(self, var: float or int) -> (float, float):
        return self.formula(var)


class RealSeqSignal(RealSignal):
    """
    使用迭代列表构建信号
    """

    def __init__(self, seq: list or tuple, *args, **kwargs):
        """
        :param seq: 可迭代的数据列表
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        """
        self.seq = seq
        super(RealSeqSignal, self).__init__(*args, **kwargs)

    def __kernel__(self, var: float or int) -> float:
        var = int((var - self.start) / self.delta)
        return self.seq[var] if var < len(self.seq) else 0


class PluralSeqSignal(PluralSignal):
    # 使用复数迭代列表构建信号

    def __init__(self, seq: list or tuple, *args, **kwargs):
        """
        :param seq: 可迭代的数据列表
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        """
        self.seq = seq
        super(PluralSeqSignal, self).__init__(*args, **kwargs)

    def __kernel__(self, var: float or int) -> (float, float):
        var = int((var - self.start) / self.delta)
        return self.seq[var] if var < len(self.seq) else 0, 0


class SamplerSignal(RealSignal):
    # 采样信号

    def __init__(self, *args, **kwargs):
        """
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        """
        super(SamplerSignal, self).__init__(*args, **kwargs)

    def __kernel__(self, var: float or int) -> float:
        return math.sin(var) / var
