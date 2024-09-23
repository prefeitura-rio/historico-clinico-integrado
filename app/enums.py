# -*- coding: utf-8 -*-
from enum import Enum


class PermitionEnum(str, Enum):
    PIPELINE_READ = "pipeline_read"
    PIPELINE_WRITE = "pipeline_write"
    PIPELINE_READWRITE = "pipeline_readwrite"
    HCI_SAME_CPF = "only_from_same_cpf"
    HCI_SAME_HEALTHUNIT = "only_from_same_unit"
    HCI_SAME_AP = "only_from_same_ap"
    HCI_FULL_PERMITION = "full_permition"


class ConditionCodeTypeEnum(str, Enum):
    CID = "cid"
    CIAP = "ciap"


class SystemEnum(str, Enum):
    VITACARE = "vitacare"
    VITAI = "vitai"
    PRONTUARIO = "prontuario"
    SMSRIO = "smsrio"
    ESUS = "esus"
    MV = "mv"
    WARELINE = "wareline"
    MEDCLINIC = "medclinic"
    SARAH = "sarah"
    NA = "nao se aplica"
    PAPEL = "papel"


class ClinicalStatusEnum(str, Enum):
    RESOLVED = "resolved"
    RESOLVING = "resolving"
    NOT_RESOLVED = "not_resolved"


class CategoryEnum(str, Enum):
    PROBLEM_LIST_ITEM = "problem-list-item"
    ENCOUTER_DIAGNOSIS = "encounter-diagnosis"


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class RaceEnum(str, Enum):
    BRANCA = "branca"
    PRETA = "preta"
    PARDA = "parda"
    AMARELA = "amarela"
    INDIGENA = "indigena"


class NationalityEnum(str, Enum):
    BRASILEIRO = "B"
    ESTRANGEIRO = "E"
    NATURALIZADO = "N"
