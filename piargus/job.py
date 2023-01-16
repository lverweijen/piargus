from pathlib import Path
from tempfile import TemporaryDirectory

from .batchwriter import BatchWriter
from .inputdata import InputData
from .table import Table


class Job:
    def __init__(self, input_data: InputData, tables=None, metadata=None, safety_rules=None,
                 suppress_method='GH', suppress_method_args=None,
                 directory=None, name=None, logbook=True, interactive=False):
        """A job to protect a data source.

        This class takes care of generating all input/meta files that TauArgus needs.
        If a directory is supplied, the necessary files will be created in that directory.
        Otherwise, a temporary directory is created, but it's better to always supply one.
        Existing files won't be written to `directory`.
        For example, metadata created from MetaData.from_rda("otherdir/metadata.rda") will use the existing file.

        :param input_data: The source from which to generate tables. Needs to be either MicroData or TableData.
        :param tables: The tables to be generated. Can be omitted if input_data is TableData.
        :param metadata: The metadata of input_data. If omitted, it will be derived from input_data.
        :param safety_rules: Rules for primary suppression. (See Table for details)
        :param suppress_method: The default method to use for secondary suppression if none is specified on table.
        If None and no suppress_method is specificed on the table, no secondary suppression is done.
        See the Tau-Argus manual for details.
        :param suppress_method_args: Parameters for suppress_method
        :param directory: Where to write tau-argus files
        :param name: Name from which to derive the name of some temporary files
        :param logbook: Whether this job should create its own logging file
        :param interactive: Whether the gui should be opened
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
        self.interactive = interactive

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
            self._setup_apriories()
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

    def _setup_apriories(self):
        for table in self.tables:
            if table.apriori is not None and table.apriori.filepath is None:
                default = self.directory / 'input' / f'apriori_{table.name}.hst'
                table.apriori.to_hst(default)

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
                t_safety_rules = self.safety_rules | table.safety_rules
                writer.specify_table(table.explanatory, table.response, table.shadow, table.cost, table.labda)

                if t_safety_rules:
                    writer.safety_rule(t_safety_rules)

            if isinstance(self.input_data, Table):
                writer.read_table()
            else:
                writer.read_microdata()

            for t_index, table in enumerate(self.tables, 1):
                t_method = table.suppress_method or self.suppress_method
                t_apriori = table.apriori

                if t_apriori is not None:
                    writer.apriori(t_apriori.filepath, t_index,
                                   separator=t_apriori.separator,
                                   ignore_error=t_apriori.ignore_error,
                                   expand_trivial=t_apriori.expand_trivial)

                if t_method:
                    t_method_args = table.suppress_method_args or self.suppress_method_args or METHOD_DEFAULTS[t_method]
                    writer.suppress(t_method, t_index, *t_method_args)
                writer.write_table(t_index, 2, {"AS": True}, str(table.filepath_out))

            if self.interactive:
                writer.go_interactive()


METHOD_DEFAULTS = {
    'GH': (0, 1),
    'MOD': (5, 1, 1, 1),
    'OPT': (5,),
    'NET': (),
    'RND': (0, 10, 0, 3),
    'CTA': (),
}
