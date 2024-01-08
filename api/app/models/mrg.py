# -*- coding: utf-8 -*-
from tortoise import fields
from tortoise.models import Model



class City(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=512)
    state = fields.ForeignKeyField("app.State", related_name="cities")

    class Meta:
        schema="mrg"


class Country(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=512)

    class Meta:
        schema="mrg"


class State(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=512)
    country = fields.ForeignKeyField("app.Country", related_name="states")

    class Meta:
        schema="mrg"


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

    class Meta:
        schema="mrg"


class Cns(Model):
    id = fields.UUIDField(pk=True)
    value = fields.CharField(max_length=16, unique=True)
    patient = fields.ForeignKeyField("app.Patient", related_name="cnss")
    is_main = fields.BooleanField(default=False)

    class Meta:
        schema="mrg"


class Patient(Model):
    id = fields.UUIDField(pk=True)
    cpf = fields.CharField(max_length=11, unique=True)
    active = fields.BooleanField(default=True)
    birth_city = fields.ForeignKeyField("app.City", related_name="birth_patients", null=True)
    birth_date = fields.DateField()
    deceased = fields.BooleanField(default=False)
    deceased_date = fields.DateField(null=True)
    ethnicity = fields.ForeignKeyField("app.Ethnicity", related_name="ethnicity", null=True)
    father_name = fields.CharField(max_length=512, null=True)
    gender = fields.ForeignKeyField("app.Gender", related_name="gender", null=True)
    mother_name = fields.CharField(max_length=512, null=True)
    name = fields.CharField(max_length=512)
    nationality = fields.ForeignKeyField("app.Nationality", related_name="nationality", null=True)
    naturalization = fields.CharField(max_length=512, null=True)
    protected_person = fields.BooleanField(null=True)
    race = fields.ForeignKeyField("app.Race", related_name="race", null=True)

    class Meta:
        unique_together = (("patient", "data_source"),)
        schema="mrg"


class Telecom(Model):
    id = fields.UUIDField(pk=True)
    system = fields.CharField(max_length=32, unique=True)
    use = fields.CharField(max_length=32, unique=True)
    value = fields.CharField(max_length=512)
    rank = fields.IntField(null=True)
    patient = fields.ForeignKeyField("app.Patient", related_name="telecom_patient_periods")
    period_start = fields.DateField(null=True)
    period_end = fields.DateField(null=True)

    class Meta:
        schema="mrg"


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

