# -*- coding: utf-8 -*-
from tortoise import fields
from tortoise.models import Model

from app.enums import (
    RaceEnum,
    GenderEnum,
    NationalityEnum,
    ConditionCodeTypeEnum,
    CategoryEnum,
    ClinicalStatusEnum,
    SystemEnum,
)
from app.validators import CPFValidator, PatientCodeValidator


class RawPatientRecord(Model):
    id = fields.IntField(pk=True)
    patient_cpf = fields.CharField(
        max_length=11, validators=[CPFValidator()], null=False, index=True
    )
    patient_code = fields.CharField(
        max_length=20, validators=[PatientCodeValidator()], null=False, index=True
    )
    data = fields.JSONField()
    data_source = fields.ForeignKeyField(
        "app.DataSource", related_name="raw_record_source", null=False
    )
    source_updated_at = fields.DatetimeField(null=False)
    is_valid = fields.BooleanField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True, index=True)
    creator = fields.ForeignKeyField("app.User", related_name="record_creator", null=True)

    class Meta:
        table = "raw__patientrecord"
        unique_together = ("patient_code", "data_source", "source_updated_at")


class RawPatientCondition(Model):
    id = fields.IntField(pk=True)
    patient_cpf = fields.CharField(
        max_length=11, validators=[CPFValidator()], null=False, index=True
    )
    patient_code = fields.CharField(
        max_length=20, validators=[PatientCodeValidator()], null=False, index=True
    )
    data = fields.JSONField()
    data_source = fields.ForeignKeyField(
        "app.DataSource", related_name="raw_condition_source", null=False
    )
    source_updated_at = fields.DatetimeField(null=False)
    is_valid = fields.BooleanField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True, index=True)
    creator = fields.ForeignKeyField("app.User", related_name="condition_creator", null=True)

    class Meta:
        table = "raw__patientcondition"
        unique_together = ("patient_code", "data_source", "source_updated_at")


class RawEncounter(Model):
    id = fields.IntField(pk=True)
    patient_cpf = fields.CharField(
        max_length=11, validators=[CPFValidator()], null=False, index=True
    )
    patient_code = fields.CharField(
        max_length=20, validators=[PatientCodeValidator()], null=False, index=True
    )
    data = fields.JSONField()
    data_source = fields.ForeignKeyField(
        "app.DataSource", related_name="raw_encounter_source", null=False
    )
    source_updated_at = fields.DatetimeField(null=False)
    source_id = fields.DatetimeField(null=False)
    is_valid = fields.BooleanField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True, index=True)
    creator = fields.ForeignKeyField("app.User", related_name="encounter_creator", null=True)

    class Meta:
        table = "raw__encounter"
        unique_together = ("patient_code", "data_source", "source_id")


class StandardizedPatientRecord(Model):
    id = fields.IntField(pk=True)
    patient_cpf = fields.CharField(max_length=11, validators=[CPFValidator()], index=True)
    patient_code = fields.CharField(max_length=20, validators=[PatientCodeValidator()], index=True)
    birth_date = fields.DateField()
    birth_city = fields.ForeignKeyField("app.City", related_name="birthcity_stdpatients", null=True)
    birth_state = fields.ForeignKeyField(
        "app.State", related_name="birthstate_stdpatients", null=True
    )
    birth_country = fields.ForeignKeyField(
        "app.Country", related_name="birthcountry_stdpatients", null=True
    )
    active = fields.BooleanField(default=True, null=True)
    protected_person = fields.BooleanField(null=True)
    deceased = fields.BooleanField(default=False, null=True)
    deceased_date = fields.DateField(null=True)
    father_name = fields.CharField(max_length=512, null=True)
    mother_name = fields.CharField(max_length=512, null=True)
    name = fields.CharField(max_length=512)
    race = fields.CharEnumField(enum_type=RaceEnum, null=True)
    gender = fields.CharEnumField(enum_type=GenderEnum)
    nationality = fields.CharEnumField(enum_type=NationalityEnum, null=True)
    raw_source = fields.ForeignKeyField(
        "app.RawPatientRecord", related_name="std_record_raw", null=False, index=True
    )
    cns_list = fields.JSONField(null=True)
    address_list = fields.JSONField(null=True)
    telecom_list = fields.JSONField(null=True)
    is_valid = fields.BooleanField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True, index=True)

    class Meta:
        table = "std__patientrecord"


class StandardizedPatientCondition(Model):
    id = fields.IntField(pk=True)
    patient_cpf = fields.CharField(max_length=11, validators=[CPFValidator()], index=True)
    patient_code = fields.CharField(max_length=20, validators=[PatientCodeValidator()], index=True)
    cid = fields.CharField(max_length=4)
    ciap = fields.CharField(max_length=4, null=True)
    clinical_status = fields.CharEnumField(enum_type=ClinicalStatusEnum, null=True)
    category = fields.CharEnumField(enum_type=CategoryEnum, null=True)
    date = fields.DatetimeField()
    raw_source = fields.ForeignKeyField(
        "app.RawPatientCondition", related_name="std_condition_raw", null=False, index=True
    )
    is_valid = fields.BooleanField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True, index=True)

    class Meta:
        table = "std__patientcondition"


class DataSource(Model):
    cnes = fields.CharField(max_length=50, unique=True, pk=True)
    system = fields.CharEnumField(SystemEnum, index=True)
    description = fields.CharField(max_length=512)


class ConditionCode(Model):
    id = fields.IntField(pk=True)
    type = fields.CharEnumField(enum_type=ConditionCodeTypeEnum, null=False)
    value = fields.CharField(max_length=5, null=False)
    description = fields.CharField(max_length=512)

    class Meta:
        unique_together = ("type", "value")


class City(Model):
    code = fields.CharField(max_length=10, pk=True)
    name = fields.CharField(max_length=512)
    state = fields.ForeignKeyField("app.State", related_name="cities")


class Country(Model):
    code = fields.CharField(max_length=10, pk=True)
    name = fields.CharField(max_length=512)


class State(Model):
    code = fields.CharField(max_length=10, pk=True)
    name = fields.CharField(max_length=512)
    country = fields.ForeignKeyField("app.Country", related_name="states")


class Gender(Model):
    id = fields.IntField(pk=True)
    slug = fields.CharEnumField(enum_type=GenderEnum, unique=True)
    name = fields.CharField(max_length=512)


class Race(Model):
    id = fields.IntField(pk=True)
    slug = fields.CharEnumField(enum_type=RaceEnum, unique=True)
    name = fields.CharField(max_length=512)


class Nationality(Model):
    id = fields.IntField(pk=True)
    slug = fields.CharEnumField(enum_type=NationalityEnum, unique=True)
    name = fields.CharField(max_length=512)


class MergedPatientAddress(Model):
    id = fields.IntField(pk=True)
    patient = fields.ForeignKeyField("app.MergedPatient", related_name="address_patient_periods")
    use = fields.CharField(max_length=32, null=True)
    type = fields.CharField(max_length=32, null=True)
    line = fields.CharField(max_length=1024)
    city = fields.ForeignKeyField("app.City", related_name="city")
    postal_code = fields.CharField(max_length=8, null=True)
    period_start = fields.DateField(null=True)
    period_end = fields.DateField(null=True)
    fingerprint = fields.CharField(max_length=32, null=True)

    class Meta:
        table = "mrg__patientaddress"


class MergedPatientTelecom(Model):
    id = fields.IntField(pk=True)
    patient = fields.ForeignKeyField("app.MergedPatient", related_name="telecom_patient_periods")
    system = fields.CharField(max_length=32, null=True)
    use = fields.CharField(max_length=32, null=True)
    value = fields.CharField(max_length=512)
    rank = fields.IntField(null=True)
    period_start = fields.DateField(null=True)
    period_end = fields.DateField(null=True)
    fingerprint = fields.CharField(max_length=32, null=True)

    class Meta:
        table = "mrg__patienttelecom"


class MergedPatientCns(Model):
    id = fields.IntField(pk=True)
    patient = fields.ForeignKeyField("app.MergedPatient", related_name="patient_cns")
    value = fields.CharField(max_length=16, unique=True)
    is_main = fields.BooleanField(default=False)
    fingerprint = fields.CharField(max_length=32, null=True)

    class Meta:
        table = "mrg__patientcns"


class MergedPatient(Model):
    patient_code = fields.CharField(pk=True, max_length=20, validators=[PatientCodeValidator()])
    patient_cpf = fields.CharField(max_length=11, validators=[CPFValidator()])
    birth_date = fields.DateField()
    active = fields.BooleanField(default=True)
    protected_person = fields.BooleanField(null=True)
    deceased = fields.BooleanField(default=False)
    deceased_date = fields.DateField(null=True)
    father_name = fields.CharField(max_length=512, null=True)
    mother_name = fields.CharField(max_length=512, null=True)
    name = fields.CharField(max_length=512)
    social_name = fields.CharField(max_length=512, null=True)
    race = fields.ForeignKeyField("app.Race", related_name="patient_race", null=True)
    gender = fields.ForeignKeyField("app.Gender", related_name="patient_gender")
    nationality = fields.ForeignKeyField(
        "app.Nationality", related_name="patient_nationality", null=True
    )
    birth_city = fields.ForeignKeyField("app.City", related_name="birth_patients", null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "mrg__patient"


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    data_source = fields.ForeignKeyField("app.DataSource", related_name="users", null=True)
    password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class TableInitialization(Model):
    id = fields.IntField(pk=True)
    table_name = fields.CharField(max_length=255, unique=True)
    last_version = fields.IntField(null=True)

    class Meta:
        table = "meta__tableinitialization"


class HealthCareRoleFamily(Model):
    code = fields.CharField(pk=True, max_length=4)
    name = fields.CharField(max_length=512)


class ProfessionalRegistry(Model):
    code = fields.CharField(pk=True, max_length=16)
    type = fields.CharField(max_length=12)
    professional = fields.ForeignKeyField("app.HealthCareProfessional", related_name="crm_professional")


class HealthCareRole(Model):
    cbo = fields.CharField(max_length=6, pk=True)
    family = fields.ForeignKeyField("app.HealthCareRoleFamily", related_name="role_family")
    description = fields.CharField(max_length=512)
    professionals = fields.ReverseRelation["HealthCareProfessional"]


class HealthCareProfessional(Model):
    id_sus = fields.CharField(pk=True, max_length=16)
    name = fields.CharField(max_length=512)
    cns = fields.CharField(max_length=16, index=True)
    cpf = fields.CharField(max_length=11, index=True, validators=[CPFValidator()])
    role = fields.ForeignKeyField("app.HealthCareRole", related_name="professional_role")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)