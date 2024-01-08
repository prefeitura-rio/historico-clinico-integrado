# -*- coding: utf-8 -*-
from tortoise import fields
from tortoise.models import Model

from enum import Enum


class ClinicalStatusEnum(Enum):
	RESOLVED = "resolved"
	RESOLVING = "resolving"
	NOT_RESOLVED = "not_resolved"

class CategoryEnum(Enum):
	PROBLEM_LIST_ITEM = "problem-list-item"
	ENCOUTER_DIAGNOSIS = "encounter-diagnosis"


class StandardizedPatientRecord(Model):
    id                  = fields.UUIDField(pk=True)
    active              = fields.BooleanField(default=True)
    birth_city          = fields.CharField(max_length=32)
    birth_date          = fields.DateField()
    deceased            = fields.BooleanField(default=False)
    deceased_date       = fields.DateField(null=True)
    ethnicity           = fields.CharField(max_length=32)
    father_name         = fields.CharField(max_length=512, null=True)
    gender              = fields.CharField(max_length=32)
    mother_name         = fields.CharField(max_length=512, null=True)
    name                = fields.CharField(max_length=512)
    nationality         = fields.CharField(max_length=32)
    naturalization      = fields.CharField(max_length=512, null=True)
    protected_person    = fields.BooleanField(null=True)
    race                = fields.CharField(max_length=32)
    raw_source          = fields.ForeignKeyField("app.RawPatientRecord", related_name="std_record_raw")

    cns_list        = fields.JSONField()
    addresses_list  = fields.JSONField()
    telecom_list    = fields.JSONField()

    class Meta:
        schema="std"


class StandardizedPatientCondition(Model):
    id              = fields.UUIDField(pk=True)
    patient         = fields.ForeignKeyField("app.Patient", related_name="std_condition_patient")
    cid             = fields.CharField(max_length=4)
    ciap            = fields.CharField(max_length=4, null=True)
    clinical_status = fields.StrEnum()
    category        = fields.StrEnum()
    date            = fields.DatetimeField()
    created_at      = fields.DatetimeField(auto_now_add=True)
    updated_at      = fields.DatetimeField(auto_now=True)
    raw_source      = fields.ForeignKeyField("app.RawPatientCondition", related_name="std_condition_raw")

    class Meta:
        schema="std"