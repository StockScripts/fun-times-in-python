import os
import abc
import psycopg2
import datetime
import pandas as pd
from sqlalchemy import create_engine
from scripts.utilities import utils


class FileIngestion(abc.ABC):
    def __init__(self,
                 run_datetime=datetime.datetime.now()):
        self.db_connection = utils.DW_STOCKS
        self.run_datetime = run_datetime.strftime('%Y%m%d%H%M%S')
        self.ingest_datetime = run_datetime.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def place_raw_file(self) -> bool:
        return False

    @property
    def place_batch_file(self) -> bool:
        return False

    @property
    def job_name(self) -> str:
        return 'job'

    @property
    def place_with_index(self) -> bool:
        return False

    @property
    def import_directory(self) -> str:
        return ''

    @property
    def import_file_prefix(self) -> str:
        return ''

    @property
    def import_file_extension(self) -> str:
        return '.csv'

    @property
    def import_file_date_format(self) -> str:
        return '%Y%m%d%H%M%S'

    @property
    def export_folder(self) -> str:
        return ''

    @property
    def export_file_name(self) -> str:
        return 'batch_'

    @property
    def export_file_type(self) -> str:
        return '.csv'

    def export_file_path(self, job) -> str:
        file_path = self.export_folder + '/' \
                    + self.export_file_name \
                    + job + '_' \
                    + self.run_datetime \
                    + self.export_file_type
        return file_path

    @property
    def export_file_separator(self) -> str:
        return ','

    @property
    def load_to_db(self) -> bool:
        return False

    @property
    def table(self) -> str:
        return ''

    @property
    def schema(self) -> str:
        return ''

    @property
    def db_engine(self) -> str:
        return create_engine(self.db_connection)

    @property
    def append_to_table(self) -> str:
        return 'append'

    @property
    def column_mapping(self) -> dict:
        return {}

    @property
    def get_columns_in_db(self) -> dict:
        query = f'select * from {self.schema}.{self.table} limit 1'
        df = utils.query_db(query=query)
        cols = list(df.columns)
        return cols

    def add_and_order_columns(self, df) -> pd.DataFrame:
        cols = self.get_columns_in_db
        for col in cols:
            if col not in df:
                df[col] = None
        df = df[cols]
        return df

    @property
    def index(self) -> bool:
        return False

    @property
    def header_row(self) -> bool:
        return False

    @property
    def data_format(self) -> pd.DataFrame:
        return pd.DataFrame()

    @property
    def get_available_files(self) -> pd.DataFrame:
        files = []
        folders = []
        file_paths = []
        for dir_obj in os.listdir(self.import_directory):
            if os.path.isdir(self.import_directory + '/' + dir_obj):
                for file in os.listdir(self.import_directory + '/' + dir_obj):
                    files.append(file)
                    folders.append(dir_obj)
                    file_paths.append(self.import_directory + '/' + dir_obj + '/' + file)
            elif os.path.isfile(self.import_directory + '/' + dir_obj):
                files.append(dir_obj)
                folders.append(self.import_directory.rpartition('/')[2])
                file_paths.append(self.import_directory + '/' + dir_obj)

        df = pd.DataFrame(files, columns=['file_names'])
        df['folders'] = folders
        df['file_paths'] = file_paths

        df = df[df['file_names'].str.contains(self.import_file_extension)]
        df['file_dates'] = df['file_names'].str.rpartition('_')[2].str.partition(self.import_file_extension)[0]
        df['file_dates'] = pd.to_datetime(df['file_dates'], format=self.import_file_date_format)
        return df

    @property
    def get_ingest_audit(self) -> pd.DataFrame:
        query = f" select coalesce(max(ingest_datetime), '1900-01-01') as ingest_datetime" \
                + f" from audit.ingest_load_times" \
                + f" where schema_name = '{self.schema}'" \
                + f" and table_name = '{self.table}'" \
                + f" and job_name = '{self.job_name}'"
        df = utils.query_db(query=query)['ingest_datetime'].values[0]
        return df

    @property
    def get_ingest_files(self) -> pd.DataFrame:
        available_files = self.get_available_files
        last_ingest_datetime = self.get_ingest_audit
        df = available_files[available_files['file_dates'] > last_ingest_datetime]
        return df

    @property
    def insert_audit_record(self):
        query = f" INSERT INTO audit.ingest_load_times" \
                + f" (schema_name, table_name, job_name, ingest_datetime)" \
                + f" VALUES ('{self.schema}', '{self.table}', '{self.job_name}', '{self.ingest_datetime}')"
        utils.insert_record(query=query)
        return

    def clean_df(self, df) -> pd.DataFrame:
        return df

    def execute(self):
        files = self.get_ingest_files
        df = self.data_format
        for idx, row in files.iterrows():
            raw = pd.read_csv(row['file_paths'])
            df = pd.concat([df, raw], sort=False)

        df = self.clean_df(df)
        if not df.empty:
            if bool(self.column_mapping):
                df = df.rename(columns=self.column_mapping)

            if 'dw_created_at' not in df:
                df['dw_created_at'] = self.ingest_datetime

            df = self.add_and_order_columns(df)

            if self.place_batch_file:
                df.to_csv(self.export_file_path(self.job_name),
                          index=self.place_with_index,
                          header=self.header_row,
                          sep=self.export_file_separator)
                file = open(self.export_file_path(self.job_name), 'r')

                conn = psycopg2.connect(self.db_connection)
                cursor = conn.cursor()
                cursor.copy_from(file,
                                 table=f'{self.schema}.{self.table}',
                                 sep=self.export_file_separator,
                                 null='')

                conn.commit()
                cursor.close()
                conn.close()
                file.close()

            elif self.load_to_db:
                df.to_sql(
                    self.table,
                    self.db_engine,
                    schema=self.schema,
                    if_exists=self.append_to_table,
                    index=self.index)

            self.insert_audit_record
