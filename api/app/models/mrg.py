# -*- coding: utf-8 -*-
from tortoise import fields
from tortoise.models import Model

from app.models.enums import RaceEnum, GenderEnum, NationalityEnum, CategoryEnum, ClinicalStatusEnum


class City(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=512)
    state = fields.ForeignKeyField("app.State", related_name="cities")


class Country(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=512)


class State(Model):
    id = fields.UUIDField(pk=True)
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
    ethnicity           = fields.CharField(max_length=32)
    father_name         = fields.CharField(max_length=512, null=True)
    mother_name         = fields.CharField(max_length=512, null=True)
    name                = fields.CharField(max_length=512)
    naturalization      = fields.CharField(max_length=512, null=True)
    race                = fields.CharEnumField(enum_type=RaceEnum, max_length=32)
    gender              = fields.CharEnumField(enum_type=GenderEnum, max_length=32)
    nationality         = fields.CharEnumField(enum_type=NationalityEnum, max_length=1)

    birth_city = fields.ForeignKeyField("app.City", related_name="birth_patients", null=True)


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

