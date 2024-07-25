# -*- coding: utf-8 -*-
# =============================================
# Formatters that are responsible for converting 
# raw JSON records to Datalake table rows.
# =============================================
from typing import List, Tuple
from datalake.utils import flatten, register_formatter
from datalake.models import (
    SMSRioCnsProvisorio,
    SMSRioPaciente,
    SMSRioTelefone,
    VitacarePaciente,
    VitacareAtendimento,
    VitacareCondicao,
    VitacareAlergia,
    VitacareEncaminhamento,
    VitacareExameSolicitado,
    VitacareIndicador,
    VitacarePrescricao,
    VitacareVacina,
)


@register_formatter(system="smsrio", entity="patientrecords")
def format_smsrio_patient(
    raw_record: dict
) -> Tuple[List[SMSRioPaciente], List[SMSRioTelefone], List[SMSRioCnsProvisorio]]:
    # Convert source_updated_at to string
    raw_record['source_updated_at'] = str(raw_record['source_updated_at'])

    # Flatten Record
    flattened_patient = flatten(raw_record)

    # Initialize Tables
    rows = {
        "pacientes": [SMSRioPaciente(**flattened_patient)],
        "telefones": [],
        "cns_provisorio": [],
    }

    # Create Tables for List Fields
    for field_name, FieldModel in [
        ('telefones', SMSRioTelefone),
        ('cns_provisorio', SMSRioCnsProvisorio)
    ]:
        # If field not in record, skip
        if field_name not in raw_record['data']:
            continue

        for value in raw_record['data'].pop(field_name) or []:
            rows[field_name].append(
                FieldModel(
                    value=value,
                    patient_cpf=raw_record.get("patient_cpf"),
                    source_updated_at=raw_record.get("source_updated_at")
                )
            )

    return rows['pacientes'], rows['telefones'], rows['cns_provisorio']


@register_formatter(system="vitacare", entity="patientrecords")
def format_vitacare_patient(
    raw_record: dict
) -> Tuple[List[SMSRioPaciente]]:
    # Convert source_updated_at to string
    raw_record['source_updated_at'] = str(raw_record['source_updated_at'])

    flattened = flatten(raw_record, list_max_depth=0)

    return ([VitacarePaciente(**flattened)],)


@register_formatter(system="vitacare", entity="encounter")
def format_vitacare_encounter(
    raw_record: dict
) -> Tuple[
    List[VitacareAtendimento],
    List[VitacareCondicao],
    List[VitacareAlergia],
    List[VitacareEncaminhamento],
    List[VitacareExameSolicitado],
    List[VitacareIndicador],
    List[VitacarePrescricao],
    List[VitacareVacina],
]:
    # Convert source_updated_at to string
    raw_record['source_updated_at'] = str(raw_record['source_updated_at'])

    # Flatten Record
    flattened = flatten(
        raw_record,
        dict_max_depth=3,
    )

    # Initialize Tables
    rows = {
        "encounter": [VitacareAtendimento(**flattened)],
        "condicoes": [],
        "alergias_anamnese": [],
        "encaminhamentos": [],
        "exames_solicitados": [],
        "indicadores": [],
        "prescricoes": [],
        "vacinas": [],
    }

    # Create Tables for List Fields
    for field_name, FieldModel in [
        ('condicoes', VitacareCondicao),
        ('alergias_anamnese', VitacareAlergia),
        ('encaminhamentos', VitacareEncaminhamento),
        ('exames_solicitados', VitacareExameSolicitado),
        ('indicadores', VitacareIndicador),
        ('prescricoes', VitacarePrescricao),
        ('vacinas', VitacareVacina)
    ]:
        # If field not in record, skip
        if field_name not in raw_record['data']:
            continue

        for fields in raw_record['data'].pop(field_name) or []:
            rows[field_name].append(
                FieldModel(
                    patient_cpf=raw_record.get("patient_cpf"),
                    atendimento_id=raw_record.get("source_id"),
                    source_updated_at=raw_record.get("source_updated_at"),
                    **fields
                )
            )

    return tuple(rows.values())
