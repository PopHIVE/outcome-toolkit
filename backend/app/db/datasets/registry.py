import os
import pandas as pd
from typing import List, Callable, Dict, Any, Generator
from sqlalchemy.engine import Row
from app.db.database import db_session
from app.configs.settings import Directories
from app.configs.consts import COUNTRY_MID


class LoaderRegistry:
    """
    This class is a common class to register ETL functions with

    """

    def __init__(self):
        self._functions = {}
        self.valid_mids = pd.read_csv(os.path.join(Directories.STATIC_DIRECTORY, 'valid_mids.csv'))

    def register(self, name: str, version: str = None) -> Callable:
        """Decorator Function that adds the wrapped function to the registry
        and applies a name.

        Parameters
        ----------
        name : str
        version : str, optional

        Returns
        ----------
        Callable
            Wrapped Function

        Examples
        ----------
            >>> @registry.register('func_name', version='1.0')
        """

        def wrap(func):
            func.version_ = version
            self._functions[name] = func
            return func

        return wrap

    def validate_datasource(self, datasource: Dict[str, Any]) -> None:
        """Validate Data Source Config"""

        assert datasource.get('data_release') is not None, f"Data Source: {datasource['name']} is missing Release"
        assert datasource.get('data_provider') is not None, f"Data Source: {datasource['name']} is missing Release"
        assert (
            datasource.get('parser') in self._functions.keys()
        ), f"Data Source: {datasource['name']} has invalid parser class. (options: {self._functions.keys()})"

    def load_sources(
        self,
        datasources: List[Dict[str, Any]],
        root_dir: str,
        data_bundle: str,
        fill_nulls: bool = False,
    ) -> None:
        """Execute the registered functions specified in the datasources bundle.

        Parameters
        ----------
        datasources : List[Dict[str, Any]]
        root_dir : str
        data_bundle : str
        fill_nulls : bool, optional
            If True, then the table will fill all missing MIDs with Nulls.
        """

        all_records = []
        for datasource in datasources:
            print(datasource)
            # Validate Data Source
            self.validate_datasource(datasource)

            # Generate Initial Records
            func = self._functions[datasource['parser']]
            records = func(**self.parse_params(datasource['params'], root_dir))

            # Add Metadata
            records = list(
                self.add_metadata(
                    records,
                    func.version_,
                    datasource['data_release'],
                    datasource['data_provider'],
                    data_bundle,
                )
            )

            # Insert Records
            self.insert_records(records, datasource.get('upsert', False))
            all_records.extend(records)

        if fill_nulls:
            null_records = self.generate_null_records(all_records)
            self.insert_records(null_records)

    def add_metadata(
        self,
        records: List[Row],
        version: str,
        data_release: str,
        data_provider: str,
        data_bundle: str,
    ) -> Generator[Row, Any, Any]:
        """Adds the Function and Datasource Metadata to each record for Data Lineage/Auditing.

        Parameters
        ----------
        records : List[Row]
        version : str
        data_release : str
        data_provider : str
        data_bundle : str

        Yields
        ------
        Generator[Row]
        """

        for record in records:
            (
                record.etl_version,
                record.data_release,
                record.data_provider,
                record.data_bundle,
            ) = (version, data_release, data_provider, data_bundle)
            yield record

    def insert_records(self, records: List[Row], upsert: bool = False) -> None:
        """Commit the Generated Rows to the DB."""

        if upsert:
            for record in records:
                db_session.merge(record)
        else:
            db_session.bulk_save_objects(records)

        db_session.commit()

    def generate_null_records(self, records: List[Row]) -> List[Row]:
        """Generate Records with populated MID but nulled values for missing data."""

        inserted_mids = set([record.mid for record in records])

        null_records = []
        for index, row in self.valid_mids.loc[~self.valid_mids.mid.isin(inserted_mids)].iterrows():
            # Special Case - We do not need to generate null rows for Country MID.
            if row.mid == COUNTRY_MID:
                continue

            null_records.append(records[0].__class__(mid=row.mid, type=row.type))

        print(f'Inserting Null Rows for missing MIDS ({len(null_records)})')
        return null_records

    def parse_params(self, params: Dict[str, Any], root_dir: str) -> Dict[str, Any]:
        """Parse the Params from the Loaded YML Configuration."""

        params_ = {}
        for key, value in params.items():
            if '_file' in key:
                # If local read from static directory
                if key.startswith('local'):
                    params_[key] = os.path.join(Directories.STATIC_DIRECTORY, value)

                # 'Fake or Real' Files
                elif key.endswith('_fr'):
                    params_[key] = os.path.join(root_dir, Directories.USERS_AND_PROJECTS_DIRECTORY, value)
                    assert os.path.exists(params_[key]), f'File: {params_[key]} Does not exist'

                # Read from Data Bundle
                else:
                    params_[key] = os.path.join(root_dir, value)
                    assert os.path.exists(params_[key]), f'File: {params_[key]} Does not exist'
            else:
                params_[key] = value
        return params_
