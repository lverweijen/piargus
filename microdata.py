from metadata import MetaData


class MicroData:
    def __init__(self, dataset, name=None, hierarchies=None, codelists=None, safety_rules=None):
        self.dataset = dataset
        self.safety_rules = safety_rules

        if name is None:
            name = f'data_{id(self)}'

        self.name = name
        self.hierarchies = hierarchies
        self.codelists = codelists

    @property
    def safety_rules(self):
        return self._safety_rules

    @safety_rules.setter
    def safety_rules(self, value):
        if value is None:
            value = set()
        elif isinstance(value, str):
            value = set(value.split('|'))
        else:
            value = set(value)

        self._safety_rules = value


class Table:
    def __init__(self, explanatory, response='<frequency>', name=None, filepath=None, safety_rules=None, method=None, method_args=None):
        if name is None:
            name = f'table_{id(self)}'

        self.explanatory = explanatory
        self.response = response
        self.name = name
        self.filepath = filepath
        self.safety_rules = safety_rules
        self.method = method
        self.method_args = method_args

    @property
    def safety_rules(self):
        return self._safety_rules

    @safety_rules.setter
    def safety_rules(self, value):
        if value is None:
            value = set()
        elif isinstance(value, str):
            value = set(value.split('|'))
        else:
            value = set(value)

        self._safety_rules = value
