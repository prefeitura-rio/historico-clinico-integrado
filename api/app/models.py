# -*- coding: utf-8 -*-
from tortoise import fields
from tortoise.models import Model


class Address(Model):
    id = fields.UUIDField(pk=True)
    use = fields.ForeignKeyField("models.AddressUse", related_name="addresses", null=True)
    type = fields.ForeignKeyField("models.AddressType", related_name="addresses", null=True)
    line = fields.CharField(max_length=1024)
    city = fields.ForeignKeyField("models.City", related_name="addresses")
    # state: contained in city.
    postal_code = fields.CharField(max_length=8, null=True)


class AddressIndividualPeriod(Model):
    id = fields.UUIDField(pk=True)
    address = fields.ForeignKeyField("models.Address", related_name="address_individual_periods")
    individual = fields.ForeignKeyField(
        "models.Individual", related_name="address_individual_periods"
    )
    period_start = fields.DateField(null=True)
    period_end = fields.DateField(null=True)


class AddressType(Model):
    id = fields.UUIDField(pk=True)
    slug = fields.CharField(max_length=32, unique=True)
    name = fields.CharField(max_length=512)


class AddressUse(Model):
    id = fields.UUIDField(pk=True)
    slug = fields.CharField(max_length=32, unique=True)
    name = fields.CharField(max_length=512)


class City(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=512)
    state = fields.ForeignKeyField("models.State", related_name="cities")
    # country: contained in state.


class Country(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=512)


class DataSource(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=512)


class Ethnicity(Model):
    id = fields.UUIDField(pk=True)
    slug = fields.CharField(max_length=32, unique=True)
    name = fields.CharField(max_length=512)


class Gender(Model):
    id = fields.UUIDField(pk=True)
    slug = fields.CharField(max_length=32, unique=True)
    name = fields.CharField(max_length=512)


class Individual(Model):
    id = fields.UUIDField(pk=True)
    active = fields.BooleanField()
    # address: contained in address_individual_periods.
    birth_city = fields.ForeignKeyField("models.City", related_name="birth_individuals", null=True)
    # birth_country: contained in birth_city.
    birth_date = fields.DateField(null=True)
    cpf = fields.CharField(max_length=11, unique=True)
    cns = fields.CharField(max_length=16, unique=True, null=True)
    data_source = fields.ForeignKeyField("models.DataSource", related_name="individuals")
    deceased = fields.BooleanField(null=True)
    ethnicity = fields.ForeignKeyField("models.Ethnicity", related_name="individuals", null=True)
    father_name = fields.CharField(
        max_length=512, null=True
    )  # TODO. Review: can this be another Individual?
    gender = fields.ForeignKeyField("models.Gender", related_name="individuals", null=True)
    mother_name = fields.CharField(
        max_length=512, null=True
    )  # TODO. Review: can this be another Individual?
    name = fields.CharField(max_length=512)
    nationality = (
        None  # TODO. Review: isn't this the same as birth_country? or at least inferred from it?
    )
    naturalization = None  # TODO. Review: is this going to be added to the model?
    protected_person = fields.BooleanField(null=True)
    race = fields.ForeignKeyField("models.Race", related_name="individuals", null=True)
    # telecom: contained in telecom_individual_periods.


class Race(Model):
    id = fields.UUIDField(pk=True)
    slug = fields.CharField(max_length=32, unique=True)
    name = fields.CharField(max_length=512)


class State(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=512)
    country = fields.ForeignKeyField("models.Country", related_name="states")


class Telecom(Model):
    id = fields.UUIDField(pk=True)
    system = fields.ForeignKeyField("models.TelecomSystem", related_name="telecoms", null=True)
    use = fields.ForeignKeyField("models.TelecomUse", related_name="telecoms", null=True)
    value = fields.CharField(max_length=512)
    rank = None  # TODO. Review: wtf is this?


class TelecomIndividualPeriod(Model):
    id = fields.UUIDField(pk=True)
    telecom = fields.ForeignKeyField("models.Telecom", related_name="telecom_individual_periods")
    individual = fields.ForeignKeyField(
        "models.Individual", related_name="telecom_individual_periods"
    )
    period_start = fields.DateField(null=True)
    period_end = fields.DateField(null=True)


class TelecomSystem(Model):
    id = fields.UUIDField(pk=True)
    slug = fields.CharField(max_length=32, unique=True)
    name = fields.CharField(max_length=512)


class TelecomUse(Model):
    id = fields.UUIDField(pk=True)
    slug = fields.CharField(max_length=32, unique=True)
    name = fields.CharField(max_length=512)
