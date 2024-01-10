# -*- coding: utf-8 -*-
from tortoise import fields
from tortoise.models import Model

from app.models.enums import RaceEnum, GenderEnum, NationalityEnum, CategoryEnum, ClinicalStatusEnum


class StandardizedPatientRecord(Model):
    id                  = fields.UUIDField(pk=True)
    patient_cpf         = fields.CharField(max_length=11)
    birth_city          = fields.CharField(max_length=32)
    birth_date          = fields.DateField()
    active              = fields.BooleanField(default=True)
    protected_person    = fields.BooleanField(null=True)
    deceased            = fields.BooleanField(default=False)
    deceased_date       = fields.DateField(null=True)
    ethnicity           = fields.CharField(max_length=32)
    father_name         = fields.CharField(max_length=512, null=True)
    mother_name         = fields.CharField(max_length=512, null=True)
    name                = fields.CharField(max_length=512)
    naturalization      = fields.CharField(max_length=512, null=True)
    race                = fields.CharEnumField(enum_type=RaceEnum)
    gender              = fields.CharEnumField(enum_type=GenderEnum)
    nationality         = fields.CharEnumField(enum_type=NationalityEnum)
    raw_source          = fields.ForeignKeyField("app.RawPatientRecord", related_name="std_record_raw")

    cns_list        = fields.JSONField(null=True)
    addresses_list  = fields.JSONField(null=True)
    telecom_list    = fields.JSONField(null=True)

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
    created_at      = fields.DatetimeField(auto_now_add=True)
    updated_at      = fields.DatetimeField(auto_now=True)
    raw_source      = fields.ForeignKeyField("app.RawPatientCondition", related_name="std_condition_raw")

    class Meta:
        table="std__patientcondition"