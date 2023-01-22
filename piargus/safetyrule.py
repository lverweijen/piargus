import functools
import inspect
from typing import Sequence


class SafetyRule:
    def __init__(self, code, check_function, maximum=None, dummy=None):
        self.code = code
        self.check_function = check_function
        self.maximum = maximum
        self.dummy = dummy

    def __repr__(self):
        return f"<SafetyRule: {self}>"

    def __str__(self):
        sig = inspect.signature(self.check_function)
        param_str = ", ".join(sig.parameters)
        return f"{self.__name__}({param_str})"

    def __call__(self, *args, **kwargs):
        sig = inspect.signature(self.check_function)
        ba = sig.bind(*args, **kwargs)
        ba.apply_defaults()

        values = self.check_function(*ba.args, **ba.kwargs)
        if values is None:
            values = tuple(ba.arguments.values())
            
        if len(values) == 1:
            (value,) = values
            return f"{self.code}({value})"
        else:
            return f"{self.code}{values}"


def safety_rule(code, maximum=None, dummy=None):
    def accept_function(check_function):
        rule = SafetyRule(code, check_function, maximum, dummy)
        functools.update_wrapper(rule, check_function)
        return rule

    return accept_function


@safety_rule("NK", maximum=2, dummy="NK(0, 0)")
def dominance_rule(n=3, k=75):
    if n < 1:
        raise ValueError("n should be positive")
    if not (0 <= k <= 100):
        raise ValueError("k should be a percentage")


@safety_rule("P", maximum=2, dummy="P(0, 0)")
def p_rule(p, n=1):
    if n < 1:
        raise ValueError("n should be positive")
    if not (0 <= p <= 100):
        raise ValueError("p should be a percentage")


@safety_rule("FREQ", maximum=1, dummy="FREQ(0, 0)")
def frequency_rule(n, safety_range):
    if n < 1:
        raise ValueError("n should be positive")
    if not (0 <= safety_range <= 100):
        raise ValueError("safety_range should be a percentage")


@safety_rule("REQ", maximum=1, dummy="REQ(0, 0, 0)")
def request_rule(percent1, percent2, safety_margin):
    if not (0 <= percent1 <= 100):
        raise ValueError("percent1 should be a percentage")
    if not (0 <= percent2 <= 100):
        raise ValueError("percent2 should be a percentage")


@safety_rule("ZERO", maximum=1)
def zero_rule(safety_range):
    pass  # TODO Unclear from manual how to use safety_range and what to check


@safety_rule("MIS")
def missing_rule(is_safe=False):
    return int(is_safe),


@safety_rule("WGT")
def weight_rule(apply_weights=False):
    return int(apply_weights),


@safety_rule("MAN")
def manual_rule(margin=20):
    if not (0 <= margin <= 100):
        raise ValueError("margin should be a percentage")


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


def join_rules_with_holding(rules_individual, rules_holding) -> Sequence[str]:
    """
    Join rules on individual level and holding level.

    Create a safety rules from the rules on an individual level and on holding level.
    """
    dummy_rules = []  # Boundary between individual and holding rules
    for rule in RULES:
        i_match = [i_rule for i_rule in rules_individual
                   if i_rule.startswith(rule.code)]
        h_match = [h_rule for h_rule in rules_holding
                   if h_rule.startswith(rule.code)]

        if rule.maximum is not None:
            if len(i_match) > rule.maximum:
                raise ValueError(f"Rule {rule.code} can only appear {rule.maximum} times.")
            if len(h_match) > rule.maximum:
                raise ValueError(f"Rule {rule.code} can only appear {rule.maximum} times.")

            if rule.dummy is not None and len(h_match) > 0:
                n_dummies = rule.maximum - len(i_match)
                dummy_rules.extend(n_dummies * [rule.dummy])

    safety_rules = list(rules_individual)
    safety_rules.extend(dummy_rules)
    safety_rules.extend(rules_holding)
    return safety_rules
