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
    VitacarePacienteHistorico,
    VitacareAtendimento,
    VitacareCondicao,
    VitacareAlergia,
    VitacareEncaminhamento,
    VitacareExameSolicitado,
    VitacareIndicador,
    VitacarePrescricao,
    VitacareVacina,
    VitacareProcedimentosClinicos
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

    # Temporary criterium to discriminate between Routine and Historic format
    if 'AP' in raw_record['data'].keys():
        return [VitacarePacienteHistorico(**flattened)]
    else:
        return [VitacarePaciente(**flattened)]


@register_formatter(system="vitacare", entity="encounter")
def format_vitacare_encounter(raw_record: dict) -> List:
    raw_record['source_updated_at'] = str(raw_record['source_updated_at'])

    flattened = flatten(raw_record,dict_max_depth=3)

    rows = [VitacareAtendimento(**flattened)]

    for field_name, FieldModel in [
        ('condicoes', VitacareCondicao),
        ('alergias_anamnese', VitacareAlergia),
        ('encaminhamentos', VitacareEncaminhamento),
        ('exames_solicitados', VitacareExameSolicitado),
        ('indicadores', VitacareIndicador),
        ('prescricoes', VitacarePrescricao),
        ('vacinas', VitacareVacina),
        ('procedimentosClinicos', VitacareProcedimentosClinicos),
    ]:
        if field_name not in raw_record['data']:
            continue

        for fields in raw_record['data'].pop(field_name) or []:
            rows.append(
                FieldModel(
                    patient_cpf=raw_record.get("patient_cpf"),
                    atendimento_id=raw_record.get("source_id"),
                    source_updated_at=raw_record.get("source_updated_at"),
                    **fields
                )
            )

    return rows