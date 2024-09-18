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
    UserClassEnum
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
    source_id = fields.CharField(max_length=100, null=False)
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
    system = fields.CharEnumField(SystemEnum, index=True, max_length=50, null=True)
    description = fields.CharField(max_length=512, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


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
    created_at = fields.DatetimeField(auto_now_add=True)

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
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "mrg__patienttelecom"


class MergedPatientCns(Model):
    id = fields.IntField(pk=True)
    patient = fields.ForeignKeyField("app.MergedPatient", related_name="patient_cns")
    value = fields.CharField(max_length=16, unique=True)
    is_main = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

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


class TableInitialization(Model):
    id = fields.IntField(pk=True)
    table_name = fields.CharField(max_length=255, unique=True)
    last_version = fields.IntField(null=True)

    class Meta:
        table = "meta__tableinitialization"


class OccupationFamily(Model):
    code = fields.CharField(pk=True, max_length=4)
    name = fields.CharField(max_length=512)


class ProfessionalRegistry(Model):
    code = fields.CharField(pk=True, max_length=16)
    type = fields.CharField(max_length=12, null=True)
    professional = fields.ForeignKeyField("app.HealthCareProfessional", related_name="professional_registry")


class Occupation(Model):
    cbo = fields.CharField(max_length=6, pk=True)
    family = fields.ForeignKeyField("app.OccupationFamily", related_name="role_family")
    description = fields.CharField(max_length=512)

class HealthCareProfessional(Model):
    id_sus = fields.CharField(pk=True, max_length=16)
    name = fields.CharField(max_length=512)
    cns = fields.CharField(max_length=16, index=True)
    cpf = fields.CharField(max_length=11, index=True, null=True, validators=[CPFValidator()])
    roles = fields.ManyToManyField("app.Occupation", related_name="professional_roles")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

class HealthCareProfessionalOccupation(Model):
    professional = fields.ForeignKeyField("app.HealthCareProfessional", related_name="professional_occcupation")
    role = fields.ForeignKeyField("app.Occupation", related_name="professional_role")

    class Meta:
        table = "healthcareprofessional_occupation"
        unique_together = ("professional", "role")

class HealthCareTeamType(Model):
    code = fields.CharField(pk=True, max_length=4)
    name = fields.CharField(max_length=512)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

class HealthCareTeam(Model):
    ine_code = fields.CharField(pk=True, max_length=10)
    name = fields.CharField(max_length=512)
    healthcare_unit = fields.ForeignKeyField("app.DataSource", related_name="team_datasource")
    team_type = fields.ForeignKeyField("app.HealthCareTeamType", related_name="team_type")
    phone = fields.CharField(max_length=16, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

class HealthCareProfessionalTeam(Model):
    professional = fields.ForeignKeyField("app.HealthCareProfessional", related_name="professional_team")
    team = fields.ForeignKeyField("app.HealthCareTeam", related_name="team_professional")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "healthcareprofessional_team"
        unique_together = ("professional", "team")


# ============================================
# User Management
# ============================================

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    name = fields.CharField(max_length=255, null=True)
    cpf = fields.CharField(max_length=11, unique=True, null=True, validators=[CPFValidator()])
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255)
    data_source = fields.ForeignKeyField("app.DataSource", related_name="users", null=True)
    role = fields.ForeignKeyField("app.SystemRole", related_name="user_role", null=True)
    # 2FA
    secret_key = fields.CharField(max_length=255, null=True)
    is_2fa_required = fields.BooleanField(default=False)
    is_2fa_activated = fields.BooleanField(default=False)
    # Metadata
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class UserHistory(Model):
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("app.User", related_name="histories")
    method = fields.CharField(max_length=10)
    path = fields.CharField(max_length=100)
    query_params = fields.JSONField(null=True)
    body = fields.JSONField(null=True)
    status_code = fields.IntField()
    timestamp = fields.DatetimeField(auto_now_add=True)


class SystemRole(Model):
    id = fields.IntField(pk=True)
    type = fields.CharEnumField(enum_type=UserClassEnum, null=True, default=UserClassEnum.PIPELINE_USER)
    slug = fields.CharField(max_length=255, unique=True)
    job_title = fields.CharField(max_length=255, null=True)
    role_title = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)