# -*- coding: utf-8 -*-
from typing import Optional, List
from pydantic import BaseModel


# Clinic Family model
class FamilyClinic(BaseModel):
    cnes: str
    name: str


# Family Health Team model
class FamilyHealthTeam(BaseModel):
    ine_code: str
    name: str


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
    username: str
    email: str


class PatientHeader(BaseModel):
    registration_name: str
    social_name: Optional[str]
    cpf: Optional[str]
    cns: Optional[str]
    birth_date: Optional[str]
    gender: Optional[str]
    race: Optional[str]
    phone: Optional[str]
    family_clinic: FamilyClinic
    family_health_team: FamilyHealthTeam
    medical_responsible: Optional[str]
    nursing_responsible: Optional[str]
    validated: bool
