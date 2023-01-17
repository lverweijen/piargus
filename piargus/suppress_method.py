class SuppressMethod:
    def __init__(self, name, args=()):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"{self.__class__.__name__}{self.name, self.args}"

    def __str__(self):
        if self.args:
            arg_str = ", ".join(map(str, self.args))
            return f"{self.name}(<table>, {arg_str})"
        else:
            return f"{self.name}(<table>)"


def ghmiter(bounds_percentage=0, model_size=1, apply_singleton=None):
    """
    Apply ghmiter.

    :param bounds_percentage: A priori bounds percentage
    :param model_size: 0 = normal, 1 indicates the large model.
    :param apply_singleton: 1 = yes,0 = no;
    default = yes if the table has frequency-information, no if not.
    """
    model_size = int(model_size)

    if not (0 <= bounds_percentage <= 100):
        raise ValueError("bounds_percentage should be a percentage")

    if apply_singleton is None:
        return SuppressMethod("GH", [bounds_percentage, model_size])
    else:
        return SuppressMethod("GH", [bounds_percentage, model_size, int(apply_singleton)])


def modular(time_per_subtable=5, single_single=True, single_multiple=True, min_freq=True):
    """Modular suppression."""
    if time_per_subtable < 0:
        raise ValueError

    return SuppressMethod("MOD", [time_per_subtable, int(single_single), int(single_multiple),
                                  int(min_freq)])


def optimal(max_time=0):
    """Optimal suppression."""
    if max_time < 0:
        raise ValueError

    return SuppressMethod("OPT", [max_time])


def network():
    """Network suppression."""
    return SuppressMethod("NET")


def rounding(rounding_base, steps=0, max_time=10, partitions=False, stop_rule=3):
    """
    Controlled rounding

    :param rounding_base:
    :param steps: number of steps allowed, normally 0 (default)
    :param max_time: Max computing time (10 = default)
    :param partitions:
    0 = no partitioning (default)
    1 = apply the partitioning procedure
    :param stop_rule:
    1 = Rapid only,
    2 = First feasible solution,
    3 = optimal solution (3 =default)
    """
    return SuppressMethod("RND", [rounding_base, steps, max_time, int(partitions), stop_rule])


def tabular_adjustment():
    """Controlled tabular adjustment."""
    return SuppressMethod("CTA")
