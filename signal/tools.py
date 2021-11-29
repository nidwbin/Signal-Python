from .base import Signal


def draw(signals: list or Signal):
    if type(signals) is list:
        for i in signals:
            i.draw()
    else:
        signals.draw()
