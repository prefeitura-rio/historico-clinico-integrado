# -*- coding: utf-8 -*-
from typing import Annotated, Literal
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.types.pydantic_models import RawDataListModel, BulkInsertOutputModel
from app.dependencies import (
    assert_user_has_pipeline_write_permition
)
from app.models import User, DataSource

from app.datalake.uploader import DatalakeUploader
from app.datalake.utils import (
    get_formatter,
    apply_formatter,
    convert_model_config_to_dict,
    WrongFormatException
)


router = APIRouter(prefix="/raw", tags=["Entidades RAW (Formato Raw/Bruto)"])


@router.post("/{entity_name}", status_code=201, response_model=BulkInsertOutputModel)
async def create_raw_data(
    entity_name: Literal["patientrecords", "patientconditions", "encounter"],
    _: Annotated[User, Depends(assert_user_has_pipeline_write_permition)],
    raw_data: RawDataListModel,
) -> BulkInsertOutputModel:

    records = raw_data.dict().get("data_list")
    data_source = await DataSource.get(cnes=raw_data.cnes)

    if data_source is None or data_source.system is None:
        return HTMLResponse(
            status_code=500,
            content=f"CNES {raw_data.cnes} is not fully configured"
        )

    # ====================
    # SEND TO DATALAKE
    # ====================
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
        if not formatter:
            return HTMLResponse(
                status_code=500,
                content=f"Formatter not found for {entity_name} and {data_source.cnes}"
            )
        for config, dataframe in apply_formatter(records, formatter).items():
            uploader = DatalakeUploader()
            await uploader.upload(
                dataframe=dataframe,
                config=convert_model_config_to_dict(config)
            )
        datalake_status['success'] = True
        datalake_status['message'] = "Data uploaded to Datalake"
    except WrongFormatException as e:
        return HTMLResponse(status_code=400, content=f"Invalid Format: {e}")
    except Exception as e:
        return HTMLResponse(status_code=500, content=f"Error in upload ({entity_name, data_source.cnes}): {e}")

    return BulkInsertOutputModel(
        count=len(records),
        datalake_status=datalake_status,
    )
