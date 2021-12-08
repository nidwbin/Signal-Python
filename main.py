import math

from signal.signals import SamplerSignal, RealFormulaSignal, PluralFormulaSignal


class X_S:
    def __init__(self, k, Ts, omega_s):
        self.k = k
        self.Ts = Ts
        self.omega_s = omega_s

    def __call__(self, omega_div_pi):
        return 2e3 / (self.Ts * (1e6 + (omega_div_pi * math.pi - self.k * self.omega_s) ** 2))


class SA:
    def __init__(self, n, Ts, x_a_nTs):
        self.n = n
        self.Ts = Ts
        self.x_a_nTs = x_a_nTs

    def __call__(self, t):
        tmp = math.pi * (t / self.Ts - self.n)
        return self.x_a_nTs * math.sin(tmp) / tmp if tmp != 0 else self.x_a_nTs


if __name__ == '__main__':
    sample_rate = 2000
    draw_rate = 0.1
    Ts = 1 / sample_rate
    omega_s = 2 * math.pi * sample_rate
    x_a_t = RealFormulaSignal(lambda t: math.exp(-1000 * abs(t)), start_time=-0.01, end_time=0.01, signal_type=float,
                              rate=10000)
    x_a_t.update(x_label=r'$x_a(t)$', t_label=r'$t$')
    x_a_t.draw()
    delta_t = RealFormulaSignal(lambda t: 1, start_time=x_a_t.start_time, end_time=x_a_t.end_time, rate=sample_rate)
    delta_t.update(x_label=r'$\delta(t)$', t_label=r'$t$')
    delta_t.draw()

    sampler_signal_t = x_a_t * delta_t

    sampler_signal_t.update(x_label=r'$x(n)$', t_label=r'$n$')
    sampler_signal_t.draw()

    X_a_f = RealFormulaSignal(lambda omega_div_pi: 2e3 / (1e6 + (omega_div_pi * math.pi) ** 2), -5000, 5000,
                              signal_type=float, rate=draw_rate)
    X_a_f.update(x_label=r'$X_a(\Omega)$', t_label=r'$\Omega/\pi$')
    X_a_f.draw()

    X_s_f = RealFormulaSignal(lambda x: 0, 0, 0, signal_type=float, rate=draw_rate)
    for k in range(-1, 2):
        tmp = RealFormulaSignal(X_S(k, Ts, omega_s),
                                -5000 + k * omega_s / math.pi, 5000 + k * omega_s / math.pi,
                                signal_type=float, rate=draw_rate)
        X_s_f = X_s_f + tmp
    X_s_f.update(x_label=r'$X_s(\Omega)$', t_label=r'$\Omega/\pi$')
    X_s_f.draw()
    x_a_t_ = RealFormulaSignal(lambda x: 0, start_time=x_a_t.start_time, end_time=x_a_t.end_time, signal_type=float,
                               rate=x_a_t.rate)
    sampler_signal_t.solve()
    n_min = int(min(sampler_signal_t.time_list) / Ts)
    n_max = int(max(sampler_signal_t.time_list) / Ts)
    for n in range(n_min, n_max + 1):
        sa = RealFormulaSignal(SA(n, Ts, sampler_signal_t[n * Ts]), start_time=x_a_t.start_time,
                               end_time=x_a_t.end_time, signal_type=float,
                               rate=x_a_t.rate)
        x_a_t_ = x_a_t_ + sa
    x_a_t_.update(x_label=r"$x'_a(t)$", t_label=r'$t$')
    x_a_t_.draw()
    deviation = x_a_t - x_a_t_
    deviation.update(x_label=r"$x_a(t)-x'_a(t)$", t_label=r't')
    deviation.draw()
