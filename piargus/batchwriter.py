from .constants import FREQUENCY_RESPONSE
from .utils import format_argument


class BatchWriter:
    """
    Helper to write a batch file for use with TauArgus.

    Usually the heavy work can be done by creating a Job.
    However, this class can still be used for direct low-level control.
    """
    def __init__(self, file):
        self._file = file
        self._commands = list()

    def write_command(self, command, arg=None):
        if arg is None:
            self._file.write(f"<{command}>\n")
        else:
            self._file.write(f"<{command}>\t{arg}\n")
        return command, arg

    def logbook(self, log_file):
        self.write_command('LOGBOOK', format_argument(log_file))

    def open_microdata(self, microdata, sep=','):
        if hasattr(microdata, 'to_csv'):
            microdata_file = f'microdata_{id(self)}.csv'
            microdata.to_csv(microdata_file, sep=sep)
        else:
            microdata_file = microdata

        return self.write_command("OPENMICRODATA", format_argument(microdata_file))

    def open_tabledata(self, tabledata):
        return self.write_command("OPENTABLEDATA", format_argument(tabledata))

    def open_metadata(self, metadata):
        return self.write_command("OPENMETADATA", format_argument(metadata))

    def specify_table(self, explanatory, response=FREQUENCY_RESPONSE, shadow=None, cost=None,
                      labda=None):
        explanatory_str = "".join([format_argument(v) for v in explanatory])
        response_str = format_argument(response)
        shadow_str = format_argument(shadow)
        cost_str = format_argument(cost)
        options = f'{explanatory_str}|{response_str}|{shadow_str}|{cost_str}'
        if labda:
            options += f"|{labda}"
        return self.write_command('SPECIFYTABLE', options)

    def read_microdata(self):
        return self.write_command("READMICRODATA")

    def read_table(self, compute_totals=None):
        if compute_totals is None:
            return self.write_command("READTABLE")
        else:
            return self.write_command("READTABLE", int(compute_totals))

    def apriori(self, filename, table, separator=',', ignore_error=False, expand_trivial=True):
        ignore_error = int(ignore_error)
        expand_trivial = int(expand_trivial)
        filename = format_argument(filename)
        separator = format_argument(separator)
        arg = f"{filename}, {table}, {separator}, {ignore_error}, {expand_trivial}"
        return self.write_command("APRIORI", arg)

    def safety_rule(self, rules):
        if isinstance(rules, str):
            rules = (rules,)
        return self.write_command('SAFETYRULE', "|".join(rules))

    def suppress(self, method, table, *method_args):
        args = ",".join(map(str, [table, *method_args]))
        return self.write_command('SUPPRESS', f"{method}({args})")

    def write_table(self, table, kind, options, filename):
        if hasattr(options, 'items'):
            options = "".join([k + {True: "+", False: "-"}[v] for k, v in options.items()])

        result = f"({table}, {kind}, {options}, {format_argument(filename)})"
        return self.write_command('WRITETABLE', result)

    def version_info(self, filename):
        return self.write_command("VERSIONINFO", format_argument(filename))

    def go_interactive(self):
        return self.write_command("GOINTERACTIVE")

    def clear(self):
        return self.write_command("CLEAR")
