from pathlib import Path
from tempfile import TemporaryDirectory

from .batchwriter import BatchWriter
from .inputdata import InputData
from .table import Table


class Job:
    def __init__(self, input_data: InputData, tables=None, metadata=None, safety_rules=None,
                 suppress_method='GH', suppress_method_args=None,
                 directory=None, name=None, logbook=True):
        """A job to protect a data source.

        This class takes care of generating all input/meta files that TauArgus needs.
        If a directory is supplied, the necessary files will be created in that directory.
        Otherwise, a temporary directory is created, but it's better to always supply one.
        Existing files won't always be written to `directory`.
        For example, metadata created by MetaData.from_rda("otherdir/metadata.rda") will use the existing file.

        When generating from microdata:
        - input_data needs to be MicroData
        - tables needs to be a list of tables

        When generating from tabular data:
        - input_data needs to be TableData
        """

        if directory is None:
            # Prevent the directory from being garbage-collected as long as this job exists
            self._tmp_directory = TemporaryDirectory(prefix='pyargus_')
            directory = Path(self._tmp_directory.name)

        if name is None:
            name = f'job_{id(self)}'

        if not isinstance(input_data, InputData):
            raise TypeError("Input needs to be MicroData or TableData")

        if tables is None:
            if isinstance(input_data, Table):
                tables = [input_data]
            else:
                raise ValueError("No outputs specified")

        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.input_data = input_data
        self.tables = tables
        self.metadata = metadata
        self.suppress_method = suppress_method
        self.suppress_method_args = suppress_method_args
        self.safety_rules = safety_rules
        self.directory = Path(directory).absolute()
        self.name = name
        self.logbook = logbook

        self._setup = False

    def __str__(self):
        return self.name

    @property
    def batch_filepath(self):
        return self.directory / f'{self.name}.arb'

    @property
    def logbook_filepath(self):
        if self.logbook is True:
            logbook = self.directory / f'{self.name}_logbook.txt'
        else:
            logbook = self.logbook

        return Path(logbook).absolute()

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

    def setup(self, reset=False):
        """Generate all files required for TauArgus to run."""
        if reset or not self._setup:
            self._setup_directories()
            self._setup_input_data()
            self._setup_hierarchies()
            self._setup_codelists()
            self._setup_metadata()
            self._setup_tables()
            self._setup_batch()
            self._setup = True

    def _setup_directories(self):
        input_directory = self.directory / 'input'
        output_directory = self.directory / 'output'
        input_directory.mkdir(exist_ok=True)
        output_directory.mkdir(exist_ok=True)

    def _setup_input_data(self):
        default = self.directory / 'input' / f"{self.input_data.name}.csv"
        if not self.input_data.filepath:
            self.input_data.to_csv(default)

    def _setup_metadata(self):
        if not self.metadata:
            self.metadata = self.input_data.generate_metadata()

        default = self.directory / 'input' / f"{self.input_data.name}.rda"
        if not self.metadata.filepath:
            self.metadata.to_rda(default)

    def _setup_hierarchies(self):
        self.input_data.resolve_column_lengths()
        for col, hierarchy in self.input_data.hierarchies.items():
            if not hierarchy.filepath:
                default = self.directory / 'input' / f'hierarchy_{col}.hrc'
                hierarchy.to_hrc(default, length=self.input_data.column_lengths[col])

    def _setup_codelists(self):
        self.input_data.resolve_column_lengths()
        for col, codelist in self.input_data.codelists.items():
            if not codelist.filepath:
                default = self.directory / 'input' / f'codelist_{col}.cdl'
                codelist.to_cdl(default, length=self.input_data.column_lengths[col])

    def _setup_tables(self):
        for table in self.tables:
            if table.filepath_out is None:
                table.filepath_out = Path(self.directory / 'output' / table.name).with_suffix('.csv')

    def _setup_batch(self):
        with open(self.batch_filepath, 'w') as batch:
            writer = BatchWriter(batch)

            if self.logbook:
                writer.logbook(self.logbook_filepath)

            if isinstance(self.input_data, Table):
                writer.open_tabledata(str(self.input_data.filepath))
            else:
                writer.open_microdata(str(self.input_data.filepath))

            writer.open_metadata(str(self.metadata.filepath))

            for table in self.tables:
                t_safety_rules = self.safety_rules | self.input_data.safety_rules | table.safety_rules
                writer.specify_table(table.explanatory, table.response, table.shadow, table.cost)
                writer.safety_rule(t_safety_rules)

            if isinstance(self.input_data, Table):
                writer.read_table()
            else:
                writer.read_microdata()

            for i, table in enumerate(self.tables, 1):
                t_method = table.suppress_method or self.suppress_method
                if t_method:
                    t_method_args = table.suppress_method_args or self.suppress_method_args or METHOD_DEFAULTS[t_method]
                    writer.suppress(t_method, i, *t_method_args)
                writer.write_table(i, 2, {"AS": True}, str(table.filepath_out))


METHOD_DEFAULTS = {
    'GH': (0, 1),
    'MOD': (5, 1, 1, 1),
    'OPT': (5,),
    'NET': (),
    'RND': (0, 10, 0, 3),
    'CTA': (),
}
