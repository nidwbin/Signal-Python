import warnings

from .base import Signal, Drawable


def __draw__(signal: Signal):
    if isinstance(signal, Drawable):
        signal.draw()
    else:
        warnings.warn("Error type.")


def draw(signals: list or Signal):
    if type(signals) is list:
        for i in signals:
            __draw__(i)
    else:
        __draw__(signals)
