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
        self.write_command('LOGBOOK', _format_string(log_file))

    def open_microdata(self, microdata, sep=','):
        if hasattr(microdata, 'to_csv'):
            microdata_file = f'microdata_{id(self)}.csv'
            microdata.to_csv(microdata_file, sep=sep)
        else:
            microdata_file = microdata

        return self.write_command("OPENMICRODATA", _format_string(microdata_file))

    def open_tabledata(self, tabledata):
        return self.write_command("OPENTABLEDATA", _format_string(tabledata))

    def open_metadata(self, metadata):
        return self.write_command("OPENMETADATA", _format_string(metadata))

    def specify_table(self, explanatory, response, shadow=None, cost=None, labda=None):
        explanatory_str = "".join([_format_string(v) for v in explanatory])
        if shadow is None:
            shadow = response
        if cost is None:
            cost = response

        response_str = _format_string(response)
        shadow_str = _format_string(shadow)
        cost_str = _format_string(cost)
        options = f'{explanatory_str}|{response_str}|{shadow_str}|{cost_str}'
        if labda:
            options += f"|{labda}"
        return self.write_command('SPECIFYTABLE', options)

    def read_microdata(self):
        return self.write_command("READMICRODATA")

    def read_table(self):
        return self.write_command("READTABLE")

    def safety_rule(self, rules):
        return self.write_command('SAFETYRULE', "|".join(rules))

    def suppress(self, method, table, *method_args):
        args = ",".join(map(str, [table, *method_args]))
        return self.write_command('SUPPRESS', f"{method}({args})")

    def write_table(self, table, kind, options, filename):
        if hasattr(options, 'items'):
            options = "".join([k + {True: "+", False: "-"}[v] for k, v in options.items()])

        result = f"({table}, {kind}, {options}, {_format_string(filename)})"
        return self.write_command('WRITETABLE', result)

    def version_info(self, filename):
        return self.write_command("VERSIONINFO", _format_string(filename))

    def go_interactive(self):
        return self.write_command("GOINTERACTIVE")

    def clear(self):
        return self.write_command("CLEAR")


def _format_string(path):
    return f'"{path!s}"'
