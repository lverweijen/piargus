from pathlib import Path
from typing import Sequence

from piargus.safetyrule import RULES


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


def format_argument(text):
    if text is None:
        return ""
    elif isinstance(text, Path):
        return f'"{text!s}"'
    elif isinstance(text, str):
        return f'"{text!s}"'
    elif isinstance(text, bool):
        return str(int(text))
    else:
        return str(text)
