from typing import List, Tuple

from datalake.utils import flatten, register_formatter
from datalake.models import (
    SMSRioCnsProvisorio,
    SMSRioPaciente,
    SMSRioTelefones,
)


@register_formatter(system="smsrio", entity="patientrecords")
def format_smsrio_patient(
    raw_record: dict
) -> Tuple[List[SMSRioPaciente], List[SMSRioTelefones], List[SMSRioCnsProvisorio]]:
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
        ('telefones', SMSRioTelefones),
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