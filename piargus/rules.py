import abc
import inspect


class SafetyRule:
    name = None

    @abc.abstractmethod
    def check_parameters(self, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        sig = inspect.signature(self.check_parameters)
        ba = sig.bind(*args, **kwargs)
        ba.apply_defaults()
        self.check_parameters(*ba.args, **ba.kwargs)
        values = tuple(v for k, v in ba.arguments.items())

        if len(values) == 1:
            (value,) = values
            return f"{self.name}({value})"
        else:
            return f"{self.name}{values}"


class Dominance(SafetyRule):
    name = "NK"

    def check_parameters(self, n=3, k=75):
        if n < 1:
            raise ValueError(f"n should be positive")
        if not (0 <= k <= 100):
            raise ValueError(f"k should be a percentage")


class P(SafetyRule):
    name = 'P'

    def check_parameters(self, p, n=1):
        if n < 1:
            raise ValueError(f"n should be positive")
        if not (0 <= p <= 100):
            raise ValueError(f"p should be a percentage")


class Zero(SafetyRule):
    name = "ZERO"

    def check_parameters(self, safety_range):
        pass  # TODO Unclear from manual how to use safety_range and what to check


class Frequency(SafetyRule):
    name = "FREQ"

    def check_parameters(self, n, safety_range):
        if n < 1:
            raise ValueError(f"n should be positive")
        if not (0 <= safety_range <= 100):
            raise ValueError(f"safety_range should be a percentage")


class Request(SafetyRule):
    name = "REQ"

    def check_parameters(self, percent1, percent2, safety_margin):
        if not (0 <= percent1 <= 100):
            raise ValueError(f"percent1 should be a percentage")
        if not (0 <= percent2 <= 100):
            raise ValueError(f"percent2 should be a percentage")


class Missing(SafetyRule):
    name = "MIS"

    def check_parameters(self, is_safe=0):
        pass

    def __call__(self, is_safe=False):
        return super().__call__(int(is_safe))


class Weight(SafetyRule):
    name = "WGT"

    def check_parameters(self, apply_weights=0):
        pass

    def __call__(self, apply_weights=False):
        return super().__call__(int(apply_weights))


class Manual(SafetyRule):
    name = "MAN"

    def check_parameters(self, margin=20):
        if not (0 <= margin <= 100):
            raise ValueError(f"margin should be a percentage")


dominance = nk = Dominance()
p = P()
zero = Zero()
frequency = freq = Frequency()
request = req = Request()
missing = mis = Missing()
weight = wgt = Weight()
manual = man = Manual()
