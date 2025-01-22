from .constants import FREQUENCY_RESPONSE
from .outputspec.safetyrule import make_safety_rule
from .helpers import format_argument


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
        """Write LOGBOOK to batch file."""
        self.write_command('LOGBOOK', format_argument(log_file))

    def open_microdata(self, microdata):
        """Write OPENMICRODATA to batch file."""
        return self.write_command("OPENMICRODATA", format_argument(microdata))

    def open_tabledata(self, tabledata):
        """Write OPENTABLEDATA to batch file."""
        return self.write_command("OPENTABLEDATA", format_argument(tabledata))

    def open_metadata(self, metadata):
        """Write METADATA to batch file."""
        metadata = getattr(metadata, "filepath", metadata)
        return self.write_command("OPENMETADATA", format_argument(metadata))

    def specify_table(
        self,
        explanatory,
        response=FREQUENCY_RESPONSE,
        shadow=None,
        cost=None,
        labda=None
    ):
        """Write SPECIFYTABLE to batch file."""
        explanatory_str = "".join([format_argument(v) for v in explanatory])
        response_str = format_argument(response)
        shadow_str = format_argument(shadow)
        cost_str = format_argument(cost)
        options = f'{explanatory_str}|{response_str}|{shadow_str}|{cost_str}'
        if labda:
            options += f"|{labda}"
        return self.write_command('SPECIFYTABLE', options)

    def read_microdata(self):
        """Write READMICRODATA to batch file."""
        return self.write_command("READMICRODATA")

    def read_table(self, compute_totals=None):
        """Write READTABLE to batch file."""
        if compute_totals is None:
            return self.write_command("READTABLE")
        else:
            return self.write_command("READTABLE", int(compute_totals))

    def apriori(self, filename, table, separator=',', ignore_error=False, expand_trivial=True):
        """Write APRIORI to batch file."""
        filename = format_argument(filename)
        table = format_argument(table)
        separator = format_argument(separator)
        ignore_error = format_argument(ignore_error)
        expand_trivial = format_argument(expand_trivial)
        arg = f"{filename}, {table}, {separator}, {ignore_error}, {expand_trivial}"
        return self.write_command("APRIORI", arg)

    def recode(self, table, variable, file_or_treelevel):
        """Write RECODE to batch file."""
        table = format_argument(table)
        variable = format_argument(variable)
        file_or_treelevel = format_argument(file_or_treelevel)
        arg = f"{table}, {variable}, {file_or_treelevel}"
        return self.write_command("RECODE", arg)

    def safety_rule(self, rule="", /, *, individual="", holding=""):
        """Write SAFETYRULE to batch file."""
        rule = make_safety_rule(rule, individual=individual, holding=holding)
        return self.write_command('SAFETYRULE', rule)

    def suppress(self, method, table, *method_args):
        """Write SUPPRESS to batch file."""
        args = ",".join(map(format_argument, [table, *method_args]))
        return self.write_command('SUPPRESS', f"{method}({args})")

    def write_table(self, table, kind, options, filename):
        """Write WRITETABLE to batch file."""
        if hasattr(options, 'items'):
            options = "".join([k + {True: "+", False: "-"}[v] for k, v in options.items()])

        result = f"({table}, {kind}, {options}, {format_argument(filename)})"
        return self.write_command('WRITETABLE', result)

    def version_info(self, filename):
        """Write VERSIONINFO to batch file."""
        return self.write_command("VERSIONINFO", format_argument(filename))

    def go_interactive(self):
        """Write GOINTERACTIVE to batch file."""
        return self.write_command("GOINTERACTIVE")

    def clear(self):
        """Write CLEAR to batch file."""
        return self.write_command("CLEAR")
