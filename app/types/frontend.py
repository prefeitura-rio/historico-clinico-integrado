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

# Condition model
class CID(BaseModel):
    status: Optional[str]
    description: Optional[str]

# Procedure model
class Procedure(BaseModel):
    description: Optional[str]
    notes: Optional[str]

# Medical Visit model
class Encounter(BaseModel):
    entry_datetime: str
    exit_datetime: Optional[str]
    location: str
    type: str
    deceased: Optional[bool]
    subtype: Optional[str]
    exhibition_type: str = "default"
    cids: List[CID]
    cids_summarized: List[str]
    responsible: Optional[Responsible]
    clinical_motivation: Optional[str]
    clinical_outcome: Optional[str]
    clinical_exams: List[ClinicalExam]
    procedures: Optional[str]
    filter_tags: List[str]
    prescription: Optional[str]
    medicines_administered: Optional[str]
    provider: Optional[str]


class UserInfo(BaseModel):
    name: Optional[str]
    cpf: Optional[str]
    username: Optional[str]
    is_use_terms_accepted: Optional[bool]
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
    deceased: Optional[bool]
    birth_date: Optional[str]
    gender: Optional[str]
    race: Optional[str]
    phone: Optional[str]
    family_clinic: FamilyClinic
    family_health_team: FamilyHealthTeam
    medical_responsible: List[Professional]
    nursing_responsible: List[Professional]
    validated: bool
