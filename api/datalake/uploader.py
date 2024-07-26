# -*- coding: utf-8 -*-
import os
import uuid
from typing import Optional
import base64

import pandas as pd
import basedosdados as bd

from loguru import logger


class DatalakeUploader:

    def __init__(
        self,
        if_exists: str = "append",
        if_storage_data_exists: str = "replace",
        dump_mode: str = "append",
        csv_delimiter: str = ";",
        force_unique_file_name: bool = False,
    ) -> None:
        self.if_exists = if_exists
        self.if_storage_data_exists = if_storage_data_exists
        self.dump_mode = dump_mode
        self.csv_delimiter = csv_delimiter
        self.force_unique_file_name = force_unique_file_name

        self._base_path = os.path.join(os.getcwd(), "files")

        self._validate_envs()

    def _validate_envs(self) -> None:
        mandatory_envs = [
            "BASEDOSDADOS_CREDENTIALS_PROD",
            "BASEDOSDADOS_CREDENTIALS_STAGING",
            "BASEDOSDADOS_CONFIG",
        ]
        missing_envs = [
            env for env in mandatory_envs if env not in os.environ
        ]
        if len(missing_envs) > 0:
            raise ValueError(f"Missing environment variables: {missing_envs}")

    def _prepare_gcp_credential(self) -> None:
        base64_credential = os.environ["BASEDOSDADOS_CREDENTIALS_PROD"]

        with open("/tmp/credentials.json", "wb") as f:
            f.write(base64.b64decode(base64_credential))

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/credentials.json"
        return


    def _split_dataframe_per_day(
        self,
        df: pd.DataFrame,
        date_column: str,
    ) -> list[tuple[pd.Timestamp, pd.DataFrame]]:
        now = pd.Timestamp.now(tz="America/Sao_Paulo")

        if df.empty:
            logger.warning("Empty dataframe. Preparing to send file with only headers")
            dfs = [(str(now.date()), df)]
        else:
            logger.warning("Non Empty dataframe. Splitting Dataframe in multiple files by day")
            df["partition_date"] = pd.to_datetime(df[date_column]).dt.date
            days = df["partition_date"].unique()
            dfs = [
                (
                    pd.Timestamp(day),
                    df[df["partition_date"] == day].drop(columns=["partition_date"]),
                )
                for day in days
            ]  # noqa

        return dfs

    def _create_file_name(
        self,
        table_id: str,
        unique: bool = False
    ) -> str:
        if unique:
            return f"{table_id}-{uuid.uuid4()}.parquet"
        else:
            return f"{table_id}.parquet"

    def _cast_to_string(self, df: pd.DataFrame) -> pd.DataFrame:
        # Cast all columns to string
        for column in df.columns:
            df[column] = df[column].astype(str)
        return df

    def _upload_files_in_folder(
        self,
        folder_path: str,
        dataset_id: str,
        table_id: str,
        source_format: str = "parquet",
        biglake_table: bool = True,
        dataset_is_public: bool = False,
    ) -> None:
        self._prepare_gcp_credential()

        tb = bd.Table(dataset_id=dataset_id, table_id=table_id)
        table_staging = f"{tb.table_full_name['staging']}"

        st = bd.Storage(dataset_id=dataset_id, table_id=table_id)
        storage_path = f"{st.bucket_name}.staging.{dataset_id}.{table_id}"
        storage_path_link = (
            f"https://console.cloud.google.com/storage/browser/{st.bucket_name}"
            f"/staging/{dataset_id}/{table_id}"
        )

        table_exists = tb.table_exists(mode="staging")

        if not table_exists:
            logger.info(f"CREATING TABLE: {dataset_id}.{table_id}")
            tb.create(
                path=folder_path,
                source_format=source_format,
                csv_delimiter=self.csv_delimiter,
                if_storage_data_exists=self.if_storage_data_exists,
                biglake_table=biglake_table,
                dataset_is_public=dataset_is_public,
            )
        else:
            if self.dump_mode == "append":
                logger.info(
                    f"TABLE ALREADY EXISTS APPENDING DATA TO STORAGE: {dataset_id}.{table_id}"
                )

                tb.append(filepath=folder_path, if_exists=self.if_exists)
            elif self.dump_mode == "overwrite":
                logger.info(
                    "MODE OVERWRITE: Table ALREADY EXISTS, DELETING OLD DATA!\n"
                    f"{storage_path}\n"
                    f"{storage_path_link}"
                )  # pylint: disable=C0301
                st.delete_table(mode="staging", bucket_name=st.bucket_name, not_found_ok=True)
                logger.info(
                    "MODE OVERWRITE: Sucessfully DELETED OLD DATA from Storage:\n"
                    f"{storage_path}\n"
                    f"{storage_path_link}"
                )  # pylint: disable=C0301
                tb.delete(mode="all")
                logger.info(
                    "MODE OVERWRITE: Sucessfully DELETED TABLE:\n" f"{table_staging}\n"
                )  # pylint: disable=C0301

                tb.create(
                    path=folder_path,
                    source_format=source_format,
                    csv_delimiter=self.csv_delimiter,
                    if_storage_data_exists=self.if_storage_data_exists,
                    biglake_table=self.biglake_table,
                    dataset_is_public=self.dataset_is_public,
                )
        logger.info("Data uploaded to BigQuery")

    def upload(
        self,
        dataframe: pd.DataFrame,
        dataset_id: str,
        table_id: str,
        biglake_table: bool = True,
        dataset_is_public: bool = False,
        partition_by_date: bool = False,
        partition_column: Optional[str] = None,
        source_format: str = "parquet",
        **kwargs
    ) -> None:
        upload_id = uuid.uuid4()
        upload_folder = os.path.join(self._base_path, str(upload_id))

        # Override values in self with kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Invalid parameter: {key}")

        if partition_by_date:
            if partition_column is None:
                raise ValueError("partition_column must be provided when partition_by_date is True")

            for partition_date, dataframe in self._split_dataframe_per_day(
                dataframe, date_column=partition_column
            ):
                year = int(partition_date.strftime("%Y"))
                month = int(partition_date.strftime("%m"))
                day = partition_date.strftime("%Y-%m-%d")

                partition_folder = f"ano_particao={year}/mes_particao={month}/data_particao={day}"

                folder_path = os.path.join(upload_folder, partition_folder)
                os.makedirs(folder_path, exist_ok=True)

                dataframe = self._cast_to_string(dataframe)
                dataframe.to_parquet(
                    os.path.join(
                        folder_path, self._create_file_name(table_id, self.force_unique_file_name)
                    )
                )
        else:
            os.makedirs(upload_folder, exist_ok=True)
            dataframe.to_parquet(
                os.path.join(
                    upload_folder, self._create_file_name(table_id, self.force_unique_file_name)
                )
            )

        self._upload_files_in_folder(
            folder_path=upload_folder,
            dataset_id=dataset_id,
            table_id=table_id,
            biglake_table=biglake_table,
            dataset_is_public=dataset_is_public,
            source_format=source_format,
        )
