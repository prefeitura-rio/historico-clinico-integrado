# -*- coding: utf-8 -*-
from enum import Enum, IntEnum

class TestEnum(IntEnum):
	TESTE1=1
	TESTE2=2

class SystemEnum(str, Enum):
	VITACARE="vitacare"
	VITAI="vitai"
	PRONTUARIO="prontuario"
	SMSRIO="smsrio"

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