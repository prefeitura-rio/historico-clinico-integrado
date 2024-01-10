# -*- coding: utf-8 -*-
from tortoise import fields
from tortoise.models import Model

from app.enums import RaceEnum, GenderEnum, NationalityEnum, ConditionCodeTypeEnum, CategoryEnum, ClinicalStatusEnum, SystemEnum



class RawPatientRecord(Model):
    id          = fields.UUIDField(pk=True)
    patient_cpf = fields.CharField(max_length=11)
    data        = fields.JSONField()
    data_source = fields.ForeignKeyField("app.DataSource", related_name="raw_record_data_source")

    created_at  = fields.DatetimeField(auto_now_add=True)
    updated_at  = fields.DatetimeField(auto_now=True)

    class Meta:
        table="raw__patientrecord"


class RawPatientCondition(Model):
    id          = fields.UUIDField(pk=True)
    patient_cpf = fields.CharField(max_length=11)
    data        = fields.JSONField()
    data_source = fields.ForeignKeyField("app.DataSource", related_name="raw_condition_data_source")

    created_at  = fields.DatetimeField(auto_now_add=True)
    updated_at  = fields.DatetimeField(auto_now=True)

    class Meta:
        table="raw__patientcondition"


class StandardizedPatientRecord(Model):
    id                  = fields.UUIDField(pk=True)
    patient_cpf         = fields.CharField(max_length=11)
    birth_city          = fields.CharField(max_length=32)
    birth_state         = fields.CharField(max_length=32)
    birth_country       = fields.CharField(max_length=32)
    birth_date          = fields.DateField()
    active              = fields.BooleanField(default=True)
    protected_person    = fields.BooleanField(null=True)
    deceased            = fields.BooleanField(default=False)
    deceased_date       = fields.DateField(null=True)
    father_name         = fields.CharField(max_length=512, null=True)
    mother_name         = fields.CharField(max_length=512, null=True)
    name                = fields.CharField(max_length=512)
    naturalization      = fields.CharField(max_length=32, null=True)
    race                = fields.CharEnumField(enum_type=RaceEnum)
    gender              = fields.CharEnumField(enum_type=GenderEnum)
    nationality         = fields.CharEnumField(enum_type=NationalityEnum)
    raw_source          = fields.ForeignKeyField("app.RawPatientRecord", related_name="std_record_raw")

    cns_list        = fields.JSONField(null=True)
    addresses_list  = fields.JSONField(null=True)
    telecom_list    = fields.JSONField(null=True)

    created_at      = fields.DatetimeField(auto_now_add=True)
    updated_at      = fields.DatetimeField(auto_now=True)

    class Meta:
        table="std__patientrecord"


class StandardizedPatientCondition(Model):
    id              = fields.UUIDField(pk=True)
    patient_cpf     = fields.CharField(max_length=11)
    cid             = fields.CharField(max_length=4)
    ciap            = fields.CharField(max_length=4, null=True)
    clinical_status = fields.CharEnumField(enum_type=ClinicalStatusEnum, max_length=32)
    category        = fields.CharEnumField(enum_type=CategoryEnum, max_length=32)
    date            = fields.DatetimeField()
    raw_source      = fields.ForeignKeyField("app.RawPatientCondition", related_name="std_condition_raw")

    created_at      = fields.DatetimeField(auto_now_add=True)
    updated_at      = fields.DatetimeField(auto_now=True)

    class Meta:
        table="std__patientcondition"


class DataSource(Model):
    id          = fields.UUIDField(pk=True)
    system      = fields.CharEnumField(SystemEnum)
    cnes        = fields.CharField(max_length=50, unique=True)
    description = fields.CharField(max_length=512)


class ConditionCode(Model):
    id = fields.UUIDField(pk=True)
    type = fields.CharEnumField(enum_type=ConditionCodeTypeEnum)
    value = fields.CharField(max_length=4)


class City(Model):
    id = fields.UUIDField(pk=True)
    code = fields.CharField(max_length=10)
    name = fields.CharField(max_length=512)
    state = fields.ForeignKeyField("app.State", related_name="cities")


class Country(Model):
    id = fields.UUIDField(pk=True)
    code = fields.CharField(max_length=10)
    name = fields.CharField(max_length=512)


class State(Model):
    id = fields.UUIDField(pk=True)
    code = fields.CharField(max_length=10)
    name = fields.CharField(max_length=512)
    country = fields.ForeignKeyField("app.Country", related_name="states")


class Address(Model):
    id = fields.UUIDField(pk=True)
    use = fields.CharField(max_length=32, unique=True)
    type = fields.CharField(max_length=32, unique=True)
    line = fields.CharField(max_length=1024)
    city = fields.ForeignKeyField("app.City", related_name="city")
    postal_code = fields.CharField(max_length=8, null=True)
    patient = fields.ForeignKeyField("app.Patient", related_name="address_patient_periods")
    period_start = fields.DateField(null=True)
    period_end = fields.DateField(null=True)


class Telecom(Model):
    id = fields.UUIDField(pk=True)
    system = fields.CharField(max_length=32, unique=True)
    use = fields.CharField(max_length=32, unique=True)
    value = fields.CharField(max_length=512)
    rank = fields.IntField(null=True)
    patient = fields.ForeignKeyField("app.Patient", related_name="telecom_patient_periods")
    period_start = fields.DateField(null=True)
    period_end = fields.DateField(null=True)


class Cns(Model):
    id = fields.UUIDField(pk=True)
    value = fields.CharField(max_length=16, unique=True)
    patient = fields.ForeignKeyField("app.Patient", related_name="cnss")
    is_main = fields.BooleanField(default=False)


class Patient(Model):
    id = fields.UUIDField(pk=True)

    patient_cpf         = fields.CharField(max_length=11, unique=True)
    birth_date          = fields.DateField()
    active              = fields.BooleanField(default=True)
    protected_person    = fields.BooleanField(null=True)
    deceased            = fields.BooleanField(default=False)
    deceased_date       = fields.DateField(null=True)
    father_name         = fields.CharField(max_length=512, null=True)
    mother_name         = fields.CharField(max_length=512, null=True)
    name                = fields.CharField(max_length=512)
    naturalization      = fields.CharField(max_length=512, null=True)
    race                = fields.CharEnumField(enum_type=RaceEnum, max_length=32)
    gender              = fields.CharEnumField(enum_type=GenderEnum, max_length=32)
    nationality         = fields.CharEnumField(enum_type=NationalityEnum, max_length=1)

    birth_city = fields.ForeignKeyField("app.City", related_name="birth_patients", null=True)


class PatientCondition(Model):
    id              = fields.UUIDField(pk=True)
    patient         = fields.ForeignKeyField("app.Patient", related_name="patientconditions")
    condition_code  = fields.ForeignKeyField("app.ConditionCode", related_name="codes")
    clinical_status = fields.CharEnumField(enum_type=ClinicalStatusEnum, max_length=32)
    category        = fields.CharEnumField(enum_type=CategoryEnum, max_length=32)
    date            = fields.DatetimeField()

    created_at      = fields.DatetimeField(auto_now_add=True)
    updated_at      = fields.DatetimeField(auto_now=True)

    class Meta:
        table="patientcondition"


class User(Model):
    id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    data_source = fields.ForeignKeyField("app.DataSource", related_name="users", null=True)
    password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

