from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Union, Mapping, Hashable, Iterable, Sequence, Any

from .batchwriter import BatchWriter
from ..helpers import slugify
from ..inputspec import InputData, TableData
from ..inputspec.hierarchy import TreeHierarchy
from ..outputspec import Table


class Job:
    """Representation a data protection task.

    This task can be fed to the tau-argus program.
    """
    def __init__(
        self,
        input_data: InputData,
        tables: Optional[Union[Mapping[Hashable, Table], Iterable[Table]]] = None,
        *,
        linked_suppress_method: Optional[str] = None,
        linked_suppress_method_args: Sequence[Any] = (),
        directory: Optional[Union[str, Path]] = None,
        name: Optional[str] = None,
        logbook: Union[bool, str] = True,
        interactive: bool = False,
        setup: bool = True,
    ):
        """
        A job to protect a data source.

        This class takes care of generating all input/meta files that TauArgus needs.
        If a directory is supplied, the necessary files will be created in that directory.
        Otherwise, a temporary directory is created, but it's better to always supply one.
        Existing files won't be written to `directory`.
        For example, if metadata is created from
        `MetaData.from_rda("otherdir/metadata.rda")`
        the existing file is used. If modifications are made to the metadata, then the user
        should call metadata.to_rda() first.

        :param input_data: The source from which to generate tables.
            Needs to be either MicroData or TableData.
        :param tables: The tables to be generated. Can be omitted if input_data is TableData.
        :param linked_suppress_method: Method to use for linked suppression.
            Options are:
                * `GHMITER` ("GH"): Hypercube
                * `MODULAR` ("MOD"): Modular

        :param linked_suppress_method_args: Parameters to pass to suppress_method.
        :param directory: Where to write tau-argus files.
        :param name: Name from which to derive the name of some temporary files.
        :param logbook: Whether this job should create its own logging file.
        :param interactive: Whether the gui should be opened.
        :param setup: Whether to set up the job immediately. (required before run).
        """

        if tables is None and isinstance(input_data, TableData):
            tables = [input_data]

        self._tmp_directory = None  # Will be used if directory is temporary
        self.directory = directory
        self.input_data = input_data
        self.tables = tables
        self.linked_suppress_method = linked_suppress_method
        self.linked_suppress_method_args = linked_suppress_method_args
        self.name = name
        self.logbook = logbook
        self.interactive = interactive

        if setup:
            self.setup()

    def __str__(self):
        return self.name

    @property
    def name(self):
        """Name of the job."""
        return self._name

    @name.setter
    def name(self, value):
        if value is None:
            value = f'job_{id(self)}'
        self._name = slugify(value)

    @property
    def directory(self):
        """Directory to put files."""
        return self._directory

    @directory.setter
    def directory(self, value):
        if value is None:
            # Prevent the directory from being garbage-collected as long as this job exists
            self._tmp_directory = TemporaryDirectory(prefix='piargus_')
            value = Path(self._tmp_directory.name)

        self._directory = Path(value).absolute()

    @property
    def input_data(self) -> InputData:
        """Inputdata for job."""
        return self._input_data

    @input_data.setter
    def input_data(self, value):
        if not isinstance(value, InputData):
            raise TypeError("Input needs to be MicroData or TableData")
        self._input_data = value

    @property
    def tables(self) -> Mapping[Hashable, Table]:
        """Which tables to generate based on input data."""
        return self._tables

    @tables.setter
    def tables(self, value):
        if not isinstance(value, Mapping):
            value = {f"table-{t}": table for t, table in enumerate(value, 1)}

        self._tables = value

    @property
    def batch_filepath(self):
        """Where the batch file will be stored (read-only).

        This is derived from name and directory.
        """
        return self.directory / f'{self.name}.arb'

    @property
    def logbook_filepath(self):
        """Where the logfile will be stored (read-only).

        This is derived automatically from name and directory.
        """
        if self.logbook is True:
            logbook = self.directory / f'{self.name}_logbook.txt'
        else:
            logbook = self.logbook

        return Path(logbook).absolute()

    @property
    def workdir(self):
        return self.directory / "work" / self.name

    def setup(self, check=True):
        """Generate all files required for TauArgus to run."""
        self._setup_directories()
        self._setup_input_data()
        self._setup_hierarchies()
        self._setup_codelists()
        self._setup_metadata()
        self._setup_tables()
        self._setup_batch()

        if check:
            self.check()

    def _setup_directories(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        input_directory = self.directory / 'input'
        output_directory = self.directory / 'output'
        input_directory.mkdir(exist_ok=True)
        output_directory.mkdir(exist_ok=True)
        self.workdir.mkdir(parents=True, exist_ok=True)

    def _setup_input_data(self):
        name = f"{self.name}_{type(self.input_data).__name__.casefold()}"
        default = self.directory / 'input' / f"{name}.csv"
        if not self.input_data.filepath:
            self.input_data.write_data(default)

    def _setup_metadata(self):
        name = f"{self.name}_{type(self.input_data).__name__.casefold()}"
        default = self.directory / 'input' / f"{name}.rda"
        if not self.input_data.metadata:
            self.input_data.write_metadata(default)

    def _setup_hierarchies(self):
        for name, col in self.input_data.items():
            if isinstance(col.hierarchy, TreeHierarchy) and not col.hierarchy.filepath:
                default = self.directory / 'input' / f'{name}_hierarchy.hrc'
                col.hierarchy.to_hrc(default, length=col.code_length)

    def _setup_codelists(self):
        for name, col in self.input_data.items():
            if col.codelist and not col.codelist.filepath:
                default = self.directory / 'input' / f'{name}_codelist.cdl'
                col.hierarchy.to_cdl(default, length=col.code_length)

    def _setup_tables(self):
        for t_name, table in self.tables.items():
            if table.filepath_out is None:
                tablename = f'{self.name}_{slugify(t_name)}'
                table.filepath_out = self.directory / 'output' / f"{tablename}.csv"

            if table.apriori and table.apriori.filepath is None:
                tablename = f'{self.name}_{slugify(t_name)}'
                default = self.directory / 'input' / f'{tablename}_apriori.hst'
                table.apriori.to_hst(default)

    def _setup_batch(self):
        with open(self.batch_filepath, 'w') as batch:
            writer = BatchWriter(batch)

            if isinstance(self.input_data, Table):
                writer.open_tabledata(self.input_data)
            else:
                writer.open_microdata(self.input_data)

            writer.open_metadata(self.input_data.metadata)

            for table in self.tables.values():
                writer.specify_table(table.explanatory, table.response, table.shadow, table.cost,
                                     table.labda)
                writer.safety_rule(table.safety_rule)

            if isinstance(self.input_data, Table):
                writer.read_table()
            else:
                writer.read_microdata()

            for t_index, table in enumerate(self.tables.values(), 1):
                if table.apriori:
                    writer.apriori(
                        table.apriori,
                        t_index,
                        separator=table.apriori.separator,
                        ignore_error=table.apriori.ignore_error,
                        expand_trivial=table.apriori.expand_trivial,
                    )

                for variable, recode in table.recodes.items():
                    writer.recode(t_index, variable, recode)

                if table.suppress_method:
                    writer.suppress(table.suppress_method, t_index, *table.suppress_method_args)

            # Linked suppression
            if self.linked_suppress_method:
                writer.suppress(self.linked_suppress_method, 0, *self.linked_suppress_method_args)

            for t_index, table in enumerate(self.tables.values(), 1):
                writer.write_table(t_index, 2, {"AS": True}, str(table.filepath_out))

            if self.interactive:
                writer.go_interactive()

    def check(self):
        problems = []
        for table in self.tables.values():
            for var in table.find_variables():
                if var not in self.input_data:
                    problems.append(f"Variable {var} not present in input_data.")

            for var in table.find_variables(categorical=True, numeric=False):
                if var in self.input_data and not self.input_data[var].recodable:
                    problems.append(f"Variable {var} not recodable. Add a hierarchy or total_code to resolve.")

            for var in table.find_variables(categorical=False, numeric=True):
                if var in self.input_data and not self.input_data[var].is_numeric:
                        problems.append(f"Variable {var} not numeric.")

        if problems:
            raise JobSetupError(problems)


class JobSetupError(Exception):
    """Exception to raise when the problem specification is wrong."""
    def __init__(self, problems):
        self.problems = problems

    def __str__(self):
        problem_str = "\n".join([f"- {problem}" for problem in self.problems])
        return f"Problems found in setup:\n{problem_str}"
