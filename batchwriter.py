class BatchWriter:
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
        self.write_command('LOGBOOK', format_path(log_file))

    def open_microdata(self, microdata, sep=','):
        if hasattr(microdata, 'to_csv'):
            microdata_file = f'microdata_{id(self)}.csv'
            microdata.to_csv(microdata_file, sep=sep)
        else:
            microdata_file = microdata

        return self.write_command("OPENMICRODATA", format_path(microdata_file))

    def open_tabledata(self, tabledata):
        return self.write_command("OPENTABLEDATA", format_path(tabledata))

    def open_metadata(self, metadata):
        return self.write_command("OPENMETADATA", format_path(metadata))

    def specify_table(self, explanatory, response, shadow=None, cost=None, labda=None):
        explanatory_str = "".join([format_string(v) for v in explanatory])
        if shadow is None:
            shadow = response
        if cost is None:
            cost = response

        response_str = format_string(response)
        shadow_str = format_string(shadow)
        cost_str = format_string(cost)
        options = f'{explanatory_str}|{response_str}|{shadow_str}|{cost_str}'
        if labda:
            options += f"|{labda}"
        return self.write_command('SPECIFYTABLE', options)

    def read_microdata(self):
        return self.write_command("READMICRODATA")

    def read_tabledata(self):
        return self.write_command("READTABLEDATA")

    def safety_rule(self, rules):
        return self.write_command('SAFETYRULE', "|".join(rules))

    def suppress(self, method, table, *method_args):
        args = ",".join(map(str, [table, *method_args]))
        return self.write_command('SUPPRESS', f"{method}({args})")

    def write_table(self, table, format, options, filename):
        if hasattr(options, 'items'):
            options = "".join([k + {True: "+", False: "-"}[v] for k, v in options.items()])

        result = f"({table}, {format}, {options}, {format_path(filename)})"
        return self.write_command('WRITETABLE', result)

    def version_info(self, filename):
        return self.write_command("VERSIONINFO", format_path(filename))


def format_path(path):
    return f'"{path!s}"'


def format_string(string):
    return f'"{string!s}"'
