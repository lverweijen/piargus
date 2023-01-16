class BatchWriter:
    """Helper to write a batch file for use with TauArgus.

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
        self.write_command('LOGBOOK', _format_arg(log_file))

    def open_microdata(self, microdata, sep=','):
        if hasattr(microdata, 'to_csv'):
            microdata_file = f'microdata_{id(self)}.csv'
            microdata.to_csv(microdata_file, sep=sep)
        else:
            microdata_file = microdata

        return self.write_command("OPENMICRODATA", _format_arg(microdata_file))

    def open_tabledata(self, tabledata):
        return self.write_command("OPENTABLEDATA", _format_arg(tabledata))

    def open_metadata(self, metadata):
        return self.write_command("OPENMETADATA", _format_arg(metadata))

    def specify_table(self, explanatory, response="<freq>", shadow=None, cost=None, labda=None):
        explanatory_str = "".join([_format_arg(v) for v in explanatory])
        response_str = _format_arg(response)
        shadow_str = _format_arg(shadow)
        cost_str = _format_arg(cost)
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
        filename = _format_arg(filename)
        separator = _format_arg(separator)
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

        result = f"({table}, {kind}, {options}, {_format_arg(filename)})"
        return self.write_command('WRITETABLE', result)

    def version_info(self, filename):
        return self.write_command("VERSIONINFO", _format_arg(filename))

    def go_interactive(self):
        return self.write_command("GOINTERACTIVE")

    def clear(self):
        return self.write_command("CLEAR")


def _format_arg(text):
    if text is None:
        return ""
    elif isinstance(text, str):
        return f'"{text!s}"'
    else:
        return repr(text)
