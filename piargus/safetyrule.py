import abc
import inspect


class SafetyRule:
    name = None
    maximum = None
    dummy = None

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


class DominanceRule(SafetyRule):
    name = "NK"
    maximum = 2
    dummy = "NK(0, 0)"

    def check_parameters(self, n=3, k=75):
        if n < 1:
            raise ValueError(f"n should be positive")
        if not (0 <= k <= 100):
            raise ValueError(f"k should be a percentage")


class PRule(SafetyRule):
    name = 'P'
    maximum = 2
    dummy = "P(0, 0)"

    def check_parameters(self, p, n=1):
        if n < 1:
            raise ValueError(f"n should be positive")
        if not (0 <= p <= 100):
            raise ValueError(f"p should be a percentage")


class FrequencyRule(SafetyRule):
    name = "FREQ"
    maximum = 1
    dummy = "FREQ(0, 0)"

    def check_parameters(self, n, safety_range):
        if n < 1:
            raise ValueError(f"n should be positive")
        if not (0 <= safety_range <= 100):
            raise ValueError(f"safety_range should be a percentage")


class RequestRule(SafetyRule):
    name = "REQ"
    maximum = 1
    dummy = "REQ(0, 0, 0)"

    def check_parameters(self, percent1, percent2, safety_margin):
        if not (0 <= percent1 <= 100):
            raise ValueError(f"percent1 should be a percentage")
        if not (0 <= percent2 <= 100):
            raise ValueError(f"percent2 should be a percentage")


class ZeroRule(SafetyRule):
    name = "ZERO"
    maximum = 1

    def check_parameters(self, safety_range):
        pass  # TODO Unclear from manual how to use safety_range and what to check


class MissingRule(SafetyRule):
    name = "MIS"

    def check_parameters(self, is_safe=0):
        pass

    def __call__(self, is_safe=False):
        return super().__call__(int(is_safe))


class WeightRule(SafetyRule):
    name = "WGT"

    def check_parameters(self, apply_weights=0):
        pass

    def __call__(self, apply_weights=False):
        return super().__call__(int(apply_weights))


class ManualRule(SafetyRule):
    name = "MAN"

    def check_parameters(self, margin=20):
        if not (0 <= margin <= 100):
            raise ValueError(f"margin should be a percentage")


dominance_rule = DominanceRule()
p_rule = PRule()
frequency_rule = FrequencyRule()
request_rule = RequestRule()
zero_rule = ZeroRule()
missing_rule = MissingRule()
weight_rule = WeightRule()
manual_rule = ManualRule()


RULES = [
    dominance_rule,
    p_rule,
    frequency_rule,
    request_rule,
    zero_rule,
    missing_rule,
    weight_rule,
    manual_rule,
]


def make_safety_rule(rules_individual, rules_holding) -> str:
    """
    Join rules on individual level and holding level.

    Create a safety rules from the rules on an individual level and on holding level.
    """
    dummy_rules = []  # Boundary between individual and holding rules
    for rule in RULES:
        i_match = [i_rule for i_rule in rules_individual
                   if i_rule.startswith(rule.name)]
        h_match = [h_rule for h_rule in rules_holding
                   if h_rule.startswith(rule.name)]

        if rule.maximum is not None:
            if len(i_match) > rule.maximum:
                raise ValueError(f"Rule {rule.name} can only appear {rule.maximum} times.")
            if len(h_match) > rule.maximum:
                raise ValueError(f"Rule {rule.name} can only appear {rule.maximum} times.")

            if rule.dummy is not None and len(h_match) > 0:
                n_dummies = rule.maximum - len(i_match)
                dummy_rules.extend(n_dummies * [rule.dummy])

    safety_rules = list(rules_individual)
    safety_rules.extend(dummy_rules)
    safety_rules.extend(rules_holding)
    return safety_rules
