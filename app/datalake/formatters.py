# -*- coding: utf-8 -*-
# =============================================
# Formatters that are responsible for converting
# raw JSON records to Datalake table rows.
# =============================================
from typing import List
from app.datalake.utils import flatten, register_formatter
from app.datalake.models import (
    SMSRioPaciente,
    VitacarePaciente,
    VitacareAtendimento
)


@register_formatter(system="smsrio", entity="patientrecords")
def format_smsrio_patient(raw_record: dict) -> List:
    raw_record['source_updated_at'] = str(raw_record['source_updated_at'])

    flattened_patient = flatten(raw_record)

    return [SMSRioPaciente(**flattened_patient)]


@register_formatter(system="vitacare", entity="patientrecords")
def format_vitacare_patient(raw_record: dict) -> List:
    raw_record['source_updated_at'] = str(raw_record['source_updated_at'])

    flattened = flatten(raw_record, list_max_depth=0)

    return [VitacarePaciente(**flattened)]


@register_formatter(system="vitacare", entity="encounter")
def format_vitacare_encounter(raw_record: dict) -> List:
    raw_record['source_updated_at'] = str(raw_record['source_updated_at'])

    flattened = flatten(raw_record, dict_max_depth=3)

    return [VitacareAtendimento(**flattened)]
