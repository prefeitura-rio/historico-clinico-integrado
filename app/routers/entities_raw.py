# -*- coding: utf-8 -*-
from typing import Annotated, Literal
from fastapi import APIRouter, Depends
from loguru import logger

from app.types.pydantic_models import RawDataListModel, BulkInsertOutputModel
from app.dependencies import (
    assert_user_has_pipeline_write_permition
)
from app.models import User, DataSource

from app.datalake.uploader import DatalakeUploader
from app.datalake.utils import (
    get_formatter,
    apply_formatter,
    convert_model_config_to_dict
)


router = APIRouter(prefix="/raw", tags=["Entidades RAW (Formato Raw/Bruto)"])


@router.post("/{entity_name}", status_code=201)
async def create_raw_data(
    entity_name: Literal["patientrecords", "patientconditions", "encounter"],
    current_user: Annotated[User, Depends(assert_user_has_pipeline_write_permition)],
    raw_data: RawDataListModel,
    upload_to_datalake: bool = True,
) -> BulkInsertOutputModel:

    records = raw_data.dict().get("data_list")
    data_source = await DataSource.get(cnes=raw_data.cnes)

    datalake_status = {
        'success': False,
        'message': None,
    }

    # Inject CNES in records
    for record in records:
        record["payload_cnes"] = data_source.cnes

    try:
        # Get Formatter
        formatter = get_formatter(
            system=data_source.system.value,
            entity=entity_name
        )
        if upload_to_datalake and formatter:
            uploader = DatalakeUploader(
                dump_mode="append",
                force_unique_file_name=True,
            )
            for config, dataframe in apply_formatter(records, formatter).items():
                uploader.upload(
                    dataframe=dataframe,
                    **convert_model_config_to_dict(config)
                )
            datalake_status['success'] = True
            datalake_status['message'] = "Data uploaded to Datalake"
    except Exception as e:
        datalake_status['success'] = True
        datalake_status['message'] = f"Error in upload ({entity_name, data_source.cnes}): {e}"
        logger.error(datalake_status['message'])

    return BulkInsertOutputModel(
        count=len(records),
        datalake_status=datalake_status,
    )
