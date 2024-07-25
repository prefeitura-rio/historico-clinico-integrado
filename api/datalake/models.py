# -*- coding: utf-8 -*-
# =============================================
# Pydantic Models Representing Datalake Tables
# =============================================
from datetime import date, datetime
from typing import Generic, Optional, List, TypeVar, Any
from pydantic import BaseModel


class SMSRioPaciente(BaseModel):
    patient_cpf: str
    source_updated_at: str
    source_id: Optional[str]
    data__nome: str
    data__nome_mae: str
    data__nome_pai: str
    data__dt_nasc: str
    data__sexo: str
    data__racaCor: str
    data__nacionalidade: str
    data__obito: str
    data__dt_obito: Optional[str]
    data__end_tp_logrado_cod: Optional[str]
    data__end_logrado: str
    data__end_numero: str
    data__end_comunidade: Optional[str]
    data__end_complem: str
    data__end_bairro: str
    data__end_cep: str
    data__cod_mun_res: Optional[str]
    data__uf_res: str
    data__cod_mun_nasc: str
    data__uf_nasc: str
    data__cod_pais_nasc: Optional[str]
    data__email: Optional[str]
    data__timestamp: str
    data__cns_provisorio: list[str]
    data__telefones: list[str]

    class Config:
        dataset_id = "brutos_plataforma_smsrio"
        table_id = "paciente_eventos"
        partition_column = "source_updated_at"


class SMSRioTelefones(BaseModel):
    patient_cpf: str
    value: str
    source_updated_at: str

    class Config:
        dataset_id = "brutos_plataforma_smsrio"
        table_id = "paciente_telefone_eventos"
        partition_column = "source_updated_at"


class SMSRioCnsProvisorio(BaseModel):
    patient_cpf: str
    value: str
    source_updated_at: str

    class Config:
        dataset_id = "brutos_plataforma_smsrio"
        table_id = "paciente_cns_eventos"
        partition_column = "source_updated_at"
    