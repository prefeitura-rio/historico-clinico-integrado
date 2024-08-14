# -*- coding: utf-8 -*-
from typing import Optional, List
from pydantic import BaseModel


# Clinic Family model
class FamilyClinic(BaseModel):
    cnes: Optional[str]
    name: Optional[str]
    phone: Optional[str]


# Family Health Team model
class FamilyHealthTeam(BaseModel):
    ine_code: Optional[str]
    name: Optional[str]
    phone: Optional[str]


# Medical Conditions model
class PatientSummary(BaseModel):
    allergies: List[str]
    continuous_use_medications: List[str]


# Responsible model
class Responsible(BaseModel):
    name: str
    role: str


# Medical Visit model
class Encounter(BaseModel):
    entry_datetime: str
    exit_datetime: str
    location: str
    type: str
    subtype: Optional[str]
    active_cids: List[str]
    responsible: Responsible
    description: Optional[str]
    filter_tags: List[str]


class UserInfo(BaseModel):
    name: Optional[str]
    cpf: Optional[str]
    username: Optional[str]
    email: Optional[str]

class Professional(BaseModel):
    name: str
    registry: Optional[str]


class PatientHeader(BaseModel):
    registration_name: str
    social_name: Optional[str]
    cpf: str
    cns: Optional[str]
    birth_date: Optional[str]
    gender: Optional[str]
    race: Optional[str]
    phone: Optional[str]
    family_clinic: FamilyClinic
    family_health_team: FamilyHealthTeam
    medical_responsible: List[Professional]
    nursing_responsible: List[Professional]
    validated: bool
