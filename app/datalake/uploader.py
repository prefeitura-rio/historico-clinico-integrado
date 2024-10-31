# -*- coding: utf-8 -*-
import os
import uuid
import shutil
import base64
from typing import Optional
from google.cloud import bigquery
from asyncify import asyncify
import pandas as pd
import basedosdados as bd

from loguru import logger

from app.datalake.utils import generate_bigquery_schema

class DatalakeUploader:

    def __init__(self) -> None:
        self._base_path = os.path.join(os.getcwd(), "files")
        self._validate_envs()

    def _validate_envs(self) -> None:
        mandatory_envs = [
            "BASEDOSDADOS_CREDENTIALS_PROD",
            "BASEDOSDADOS_CREDENTIALS_STAGING",
            "BASEDOSDADOS_CONFIG",
        ]
        missing_envs = [env for env in mandatory_envs if env not in os.environ]
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
            dfs = [(now.date(), df)]
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

    def _create_file_name(self, table_id: str, unique: bool = False) -> str:
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
        if_exists: str = "append",
        if_storage_data_exists: str = "replace",
        dump_mode: str = "append",
        csv_delimiter: str = ";",
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
                csv_delimiter=csv_delimiter,
                if_storage_data_exists=if_storage_data_exists,
                biglake_table=biglake_table,
                dataset_is_public=dataset_is_public,
            )
        else:
            if dump_mode == "append":
                logger.info(
                    f"TABLE ALREADY EXISTS APPENDING DATA TO STORAGE: {dataset_id}.{table_id}"
                )

                tb.append(filepath=folder_path, if_exists=if_exists)
            elif dump_mode == "overwrite":
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
                    csv_delimiter=csv_delimiter,
                    if_storage_data_exists=if_storage_data_exists,
                    biglake_table=biglake_table,
                    dataset_is_public=dataset_is_public,
                )
        logger.info("Data uploaded to BigQuery")

    async def _upload_as_biglake(
        self,
        dataframe: pd.DataFrame,
        dataset_id: str,
        table_id: str,
        dataset_is_public: bool = False,
        partition_by_date: bool = False,
        partition_column: Optional[str] = None,
        source_format: str = "parquet",
        force_unique_file_name: bool = False,
        **kwargs,
    ) -> None:
        biglake_table = (True,)
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
                        folder_path, self._create_file_name(table_id, force_unique_file_name)
                    )
                )
        else:
            os.makedirs(upload_folder, exist_ok=True)
            dataframe.to_parquet(
                os.path.join(
                    upload_folder, self._create_file_name(table_id, force_unique_file_name)
                )
            )

        try:
            logger.info(f"Uploading data to BigQuery: {dataset_id}.{table_id}")
            self._upload_files_in_folder(
                folder_path=upload_folder,
                dataset_id=dataset_id,
                table_id=table_id,
                biglake_table=biglake_table,
                dataset_is_public=dataset_is_public,
                source_format=source_format,
            )
        except Exception as e:
            logger.error(f"Error uploading data to BigQuery: {e}")
        finally:
            shutil.rmtree(upload_folder)

    async def _upload_as_native_table(
        self,
        dataframe: pd.DataFrame,
        dataset_id: str,
        table_id: str,
        date_partition_column: Optional[str],
        create_disposition: str = "CREATE_IF_NEEDED",
        write_disposition: str = "WRITE_APPEND",
        source_format: str = "PARQUET",
        **kwargs,
    ) -> None:
        """
        Uploads a pandas DataFrame to a Google BigQuery table as a native table.
        Args:
            dataframe (pd.DataFrame): The DataFrame to upload.
            dataset_id (str): The ID of the dataset containing the table.
            table_id (str): The ID of the table to upload the DataFrame to.
            create_disposition (str, optional): Specifies whether the table should be created
                if it does not exist. Defaults to "CREATE_IF_NEEDED".
            write_disposition (str, optional): Specifies the action that occurs if the
                destination table already exists. Defaults to "WRITE_APPEND".
            source_format (str, optional): The format of the source data. Defaults to "PARQUET".
            date_partition_column (str, optional): The name of the column to use for date
                partitioning.
        Returns:
            bool: True if the upload was successful, False otherwise.
        """
        self._prepare_gcp_credential()

        client = bigquery.Client().from_service_account_json("/tmp/credentials.json")

        dataset_ref = client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)

        job_config_params = {
            "create_disposition": create_disposition,
            "write_disposition": write_disposition,
            "source_format": source_format,
        }
        if date_partition_column:
            if date_partition_column not in dataframe.columns:
                raise ValueError(
                    f"Partition column '{date_partition_column}' not found in DataFrame columns"
                )
            
            dataframe["data_particao"] = pd.to_datetime(dataframe[date_partition_column])
            job_config_params["time_partitioning"] = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="data_particao"
            )
            job_config_params["schema"]=generate_bigquery_schema(
                dataframe,
                datetime_as="DATE"
            )

        job_result = client.load_table_from_dataframe(
            dataframe=dataframe,
            destination=table_ref,
            job_config=bigquery.LoadJobConfig(**job_config_params),
            num_retries=5,
        )
        result = await asyncify(job_result.result)()
        job = client.get_job(result.job_id)

        return job.state == "DONE"

    async def upload(self, dataframe: pd.DataFrame, config: dict) -> None:
        if config["biglake_table"]:
            await self._upload_as_biglake(dataframe, **config)
        else:
            await self._upload_as_native_table(dataframe, **config)
