# -*- coding: utf-8 -*-
from typing import Optional, List
from pydantic import BaseModel


class LoginForm(BaseModel):
    username: str
    password: str


class LoginFormWith2FA(BaseModel):
    username: str
    password: str
    totp_code: str


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


# Clinical Exam Model
class ClinicalExam(BaseModel):
    type: str
    description: Optional[str]


# Medical Conditions model
class PatientSummary(BaseModel):
    allergies: List[str]
    continuous_use_medications: List[str]


# Responsible model
class Responsible(BaseModel):
    name: Optional[str]  # Temporary
    role: str


# Medical Visit model
class Encounter(BaseModel):
    entry_datetime: str
    exit_datetime: Optional[str]
    location: str
    type: str
    subtype: Optional[str]
    exhibition_type: str = "default"
    active_cids: List[str]
    responsible: Optional[Responsible]
    clinical_motivation: Optional[str]
    clinical_outcome: Optional[str]
    clinical_exams: List[ClinicalExam]
    filter_tags: List[str]


class UserInfo(BaseModel):
    name: Optional[str]
    cpf: Optional[str]
    username: Optional[str]
    email: Optional[str]
    role: Optional[str]


class Professional(BaseModel):
    name: Optional[str]
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
