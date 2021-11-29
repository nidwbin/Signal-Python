from collections.abc import Callable
from .base import RealSignal, PluralSignal


class Impulse(RealSignal):
    """
    实数冲激信号
    """

    def __init__(self, start_time: float or int = 0, end_time: float or int = 0,
                 switch_time: float or int = None, strength: float = 1, *args, **kwargs):
        """
        :param start_time: 开始时间
        :param end_time: 停止时间
        :param switch_time: 信号状态切换时间
        :param strength: 强度
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        """
        super(Impulse, self).__init__(start_time, end_time, *args, **kwargs)
        self.strength = strength
        if switch_time is None:
            # 默认值，选开始和结束时间的中点
            if self.signal_type is int:
                self.switch_time = (self.start_time + self.end_time) // 2
            else:
                self.switch_time = (self.start_time + self.end_time) / 2
        else:
            assert self.start_time <= switch_time <= self.end_time
            self.switch_time = switch_time
        # 冲激时间与最小时间片对齐
        self.switch_time = (self.switch_time - self.start_time) // self.delta_time
        self.switch_time = self.switch_time * self.delta_time + self.start_time

    def __kernel__(self, time: float or int) -> float:
        """
        浮点数比较存在精度误差，进行容错处理，误差<=delta time
        """
        return self.strength if 0 <= time - self.switch_time < self.delta_time else 0.0


class Step(RealSignal):
    """
    实数阶跃信号
    """

    def __init__(self, start_time: float or int = 0, end_time: float or int = 0,
                 switch_time: float or int = None, strength: float = 1, *args, **kwargs):
        """
        :param start_time: 开始时间
        :param end_time: 停止时间
        :param switch_time: 信号状态切换时间
        :param strength: 强度
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        """
        super(Step, self).__init__(start_time, end_time, *args, **kwargs)
        self.strength = strength
        if switch_time is None:
            # 默认值，选开始和结束时间的中点
            if self.signal_type is int:
                self.switch_time = (self.start_time + self.end_time) // 2
            else:
                self.switch_time = (self.start_time + self.end_time) / 2
        else:
            assert self.start_time <= switch_time <= self.end_time
            self.switch_time = switch_time
        # 阶跃时间与最小时间片对齐
        self.switch_time = (self.switch_time - self.start_time) // self.delta_time
        self.switch_time = self.switch_time * self.delta_time + self.start_time

    def __kernel__(self, time: float or int) -> float:
        return self.strength if time >= self.switch_time else 0.0


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

    def __kernel__(self, time: float or int):
        return self.formula(time)


class PluralFormulaSignal(PluralSignal):
    """
    使用复数公式或函数构建信号
    """

    def __init__(self, formula: Callable[float or int], *args, **kwargs):
        """
        :param formula: 公式或函数
        :param args: 其他基类参数
        :param kwargs: 其他基类参数
        """
        self.formula = formula
        super(PluralFormulaSignal, self).__init__(*args, **kwargs)

    def __kernel__(self, time: float or int):
        return self.formula(time)
