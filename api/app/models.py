# -*- coding: utf-8 -*-
from tortoise import fields
from tortoise.exceptions import NoValuesFetched
from tortoise.models import Model

from app.pydantic_models import (
    AddressModel,
    PatientModel,
    PeriodModel,
    TelecomModel,
)


class Address(Model):
    id = fields.UUIDField(pk=True)
    use = fields.ForeignKeyField("app.AddressUse", related_name="addresses", null=True)
    type = fields.ForeignKeyField("app.AddressType", related_name="addresses", null=True)
    line = fields.CharField(max_length=1024)
    city = fields.ForeignKeyField("app.City", related_name="addresses")
    # state: contained in city.
    postal_code = fields.CharField(max_length=8, null=True)

    @classmethod
    async def create_from_pydantic_model(cls, address: AddressModel) -> "Address":
        # Dump the Pydantic model to a dict.
        address_data = address.model_dump()
        # Parse the foreign keys.
        # - use.
        if address_data["use"]:
            address_data["use"] = await AddressUse.get_or_none(slug=address_data.pop("use"))
        # - type.
        if address_data["type"]:
            address_data["type"] = await AddressType.get_or_none(slug=address_data.pop("type"))
        # - city.
        address_data["city"] = await City.get_or_none(
            name=address_data.pop("city"),
            state__name=address_data.pop("state"),
            state__country__name=address_data.pop("country"),
        )
        # Create the address.
        return await Address.create(**address_data)


class AddressPatientPeriod(Model):
    id = fields.UUIDField(pk=True)
    address = fields.ForeignKeyField("app.Address", related_name="address_patient_periods")
    patient = fields.ForeignKeyField("app.PatientRecord", related_name="address_patient_periods")
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
    state = fields.ForeignKeyField("app.State", related_name="cities")
    # country: contained in state.


class Cns(Model):
    id = fields.UUIDField(pk=True)
    value = fields.CharField(max_length=16, unique=True)
    patient = fields.ForeignKeyField("app.PatientRecord", related_name="cnss")
    is_main = fields.BooleanField(default=False)


class Country(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=512)


class DataSource(Model):
    # TODO (future): data normalization pipeline will be associated with a data source.
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


class Nationality(Model):
    id = fields.UUIDField(pk=True)
    slug = fields.CharField(max_length=32, unique=True)
    name = fields.CharField(max_length=512)


class Patient(Model):
    id = fields.UUIDField(pk=True)
    cpf = fields.CharField(max_length=11, unique=True)


class PatientRecord(Model):
    patient = fields.ForeignKeyField("app.Patient", related_name="records")
    data_source = fields.ForeignKeyField("app.DataSource", related_name="patients")

    active = fields.BooleanField(default=True)
    birth_city = fields.ForeignKeyField("app.City", related_name="birth_patients", null=True)
    birth_date = fields.DateField()
    deceased = fields.BooleanField(default=False)
    deceased_date = fields.DateField(null=True)
    ethnicity = fields.ForeignKeyField("app.Ethnicity", related_name="patients", null=True)
    father_name = fields.CharField(max_length=512, null=True)
    gender = fields.ForeignKeyField("app.Gender", related_name="patients", null=True)
    mother_name = fields.CharField(max_length=512, null=True)
    name = fields.CharField(max_length=512)
    nationality = fields.ForeignKeyField("app.Nationality", related_name="patients", null=True)
    naturalization = fields.CharField(max_length=512, null=True)
    protected_person = fields.BooleanField(null=True)
    race = fields.ForeignKeyField("app.Race", related_name="patients", null=True)

    class Meta:
        unique_together = (("patient", "data_source"),)

    @classmethod
    async def create_from_pydantic_model(cls, patient: PatientModel) -> "PatientRecord":
        # Dump the Pydantic model to a dict.
        patient_data = patient.model_dump()
        # Check if the patient already exists using the CPF
        patient_cpf = patient_data.pop("cpf")

        patient_obj: Patient = await Patient.get_or_none(cpf=patient_cpf)
        if not patient_obj:
            patient_obj = await Patient.create(cpf=patient_cpf)
        patient_data["patient"] = patient_obj

        # Start by parsing the address.
        raw_addresses = patient.address
        addresses: list[Address] = []
        if raw_addresses:
            for address in raw_addresses:
                address_obj: Address = await Address.create_from_pydantic_model(address)
                addresses.append(address_obj)
        # Parse the telecom.
        raw_telecoms = patient.telecom
        telecoms: list[Telecom] = []
        if raw_telecoms:
            for telecom in raw_telecoms:
                telecom_obj: Telecom = await Telecom.create_from_pydantic_model(telecom)
                telecoms.append(telecom_obj)
        # Now parse the foreign keys.
        # - birth_city.
        if (
            patient_data["birth_city"]
            and patient_data["birth_state"]
            and patient_data["birth_country"]
        ):
            patient_data["birth_city"] = await City.get_or_none(
                name=patient_data.pop("birth_city"),
                state__name=patient_data.pop("birth_state"),
                state__country__name=patient_data.pop("birth_country"),
            )
        else:
            patient_data.pop("birth_city")
            patient_data.pop("birth_state")
            patient_data.pop("birth_country")
        # - data_source.
        patient_data["data_source"] = await DataSource.get_or_none(
            name=patient_data.pop("data_source_name")
        )
        # - ethnicity.
        if patient_data["ethnicity"]:
            patient_data["ethnicity"] = await Ethnicity.get_or_none(
                name=patient_data.pop("ethnicity")
            )
        # - father_name.
        if patient_data["father"]:
            patient_data["father_name"] = patient_data.pop("father")
        # - gender.
        patient_data["gender"] = await Gender.get_or_none(
            slug=patient_data.pop("gender")
        )
        # - mother_name.
        if patient_data["mother"]:
            patient_data["mother_name"] = patient_data.pop("mother")
        # - nationality.
        if patient_data["nationality"]:
            patient_data["nationality"] = await Nationality.get_or_none(
                name=patient_data.pop("nationality")
            )
        # - race.
        if patient_data["race"]:
            patient_data["race"] = await Race.get_or_none(name=patient_data.pop("race"))
        # Create the patient.
        patient_record = await PatientRecord.create(**patient_data)

        patient_cns_value = patient_data.pop("cns")
        patient_cns : Cns = await Cns.get_or_none(
            patient=patient_record,
            value=patient_cns_value
        )
        if not patient_cns:
            await Cns.create(
                patient=patient_record,
                value=patient_cns_value
            )

        # Create the address_patient_periods.
        try:
            if raw_addresses:
                for address, raw_address in zip(addresses, raw_addresses):

                    # Verify existance of period value
                    if not raw_address.period:
                        period_start = None
                        period_end = None
                    else:
                        period_start = raw_address.period.start
                        period_end = raw_address.period.end

                    await AddressPatientPeriod.create(
                        address=address,
                        patient=patient_record,
                        period_start=period_start,
                        period_end=period_end,
                    )
        except Exception as exc:
            await patient_record.delete()
            raise exc
        # Create the telecom_patient_periods.
        try:
            if raw_telecoms:
                for telecom, raw_telecom in zip(telecoms, raw_telecoms):

                    # Verify existance of period value
                    if not raw_telecom.period:
                        period_start = None
                        period_end = None
                    else:
                        period_start = raw_telecom.period.start
                        period_end = raw_telecom.period.end

                    await TelecomPatientPeriod.create(
                        telecom=telecom,
                        patient=patient_record,
                        period_start=period_start,
                        period_end=period_end,
                    )
        except Exception as exc:
            await patient_record.delete()
            raise exc
        # Return the patient.
        return patient_record

    async def to_pydantic_model(self) -> PatientModel:
        # Dump the patient.
        active = self.active
        birth_city = self.birth_city.name if self.birth_city else None

        if self.birth_city.state:
            state = await self.birth_city.state
            birth_state = state.name

            if state.country:
                country = await state.country
                birth_country = country.name

        birth_date = self.birth_date
        cpf = self.patient.cpf
        # Iterate over the patient's CNSs. If there is a main CNS, use it. Otherwise, use the first
        # one.
        cnss = []
        try:
            cnss_instances = await Cns.filter(patient=self)
            for cns in cnss_instances:
                if cns.is_main:
                    cnss.insert(0, cns.value)
                else:
                    cnss.append(cns.value)
        except NoValuesFetched:
            pass
        cns = cnss[0] if cnss else None
        data_source_name = self.data_source.name
        deceased = self.deceased
        ethnicity = self.ethnicity.name if self.ethnicity else None
        father = self.father_name
        gender = self.gender.name if self.gender else None
        mother = self.mother_name
        name = self.name
        nationality = self.nationality.name if self.nationality else None
        naturalization = self.naturalization
        protected_person = self.protected_person
        race = self.race.name if self.race else None
        # Iterate over the patient's addresses.
        addresses = []
        try:
            for address_patient_period in self.address_patient_periods:
                address = address_patient_period.address
                period = PeriodModel(
                    start=address_patient_period.period_start,
                    end=address_patient_period.period_end,
                )
                addresses.append(
                    AddressModel(
                        use=address.use.name if address.use else None,
                        type=address.type.name if address.type else None,
                        line=address.line,
                        city=address.city.name,
                        state=address.city.state.name,
                        country=address.city.state.country.name,
                        postal_code=address.postal_code,
                        period=period,
                    )
                )
        except NoValuesFetched:
            pass
        # Iterate over the patient's telecoms.
        telecoms = []
        try:
            for telecom_patient_period in self.telecom_patient_periods:
                telecom = telecom_patient_period.telecom
                period = PeriodModel(
                    start=telecom_patient_period.period_start,
                    end=telecom_patient_period.period_end,
                )
                telecoms.append(
                    TelecomModel(
                        system=telecom.system.name if telecom.system else None,
                        use=telecom.use.name if telecom.use else None,
                        value=telecom.value,
                        rank=telecom.rank,
                        period=period,
                    )
                )
        except NoValuesFetched:
            pass
        # Create the Pydantic model.
        return PatientModel(
            active=active,
            address=addresses,
            birth_city=birth_city,
            birth_state=birth_state,
            birth_country=birth_country,
            birth_date=birth_date,
            cpf=cpf,
            cns=cns,
            data_source_name=data_source_name,
            deceased=deceased,
            ethnicity=ethnicity,
            father=father,
            gender=gender,
            mother=mother,
            name=name,
            nationality=nationality,
            naturalization=naturalization,
            protected_person=protected_person,
            race=race,
            telecom=telecoms,
        )


class Race(Model):
    id = fields.UUIDField(pk=True)
    slug = fields.CharField(max_length=32, unique=True)
    name = fields.CharField(max_length=512)


class RawPatientRecord(Model):
    id = fields.UUIDField(pk=True)
    data = fields.JSONField()
    data_source = fields.ForeignKeyField("app.DataSource", related_name="raw_patients")


class State(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=512)
    country = fields.ForeignKeyField("app.Country", related_name="states")


class Telecom(Model):
    id = fields.UUIDField(pk=True)
    system = fields.ForeignKeyField("app.TelecomSystem", related_name="telecoms", null=True)
    use = fields.ForeignKeyField("app.TelecomUse", related_name="telecoms", null=True)
    value = fields.CharField(max_length=512)
    rank = fields.IntField(null=True)

    @classmethod
    async def create_from_pydantic_model(cls, telecom: TelecomModel) -> "Telecom":
        # Dump the Pydantic model to a dict.
        telecom_data = telecom.model_dump()
        # Parse the foreign keys.
        # - system.
        if telecom_data["system"]:
            telecom_data["system"] = await TelecomSystem.get_or_none(
                slug=telecom_data.pop("system")
            )
        # - use.
        if telecom_data["use"]:
            telecom_data["use"] = await TelecomUse.get_or_none(slug=telecom_data.pop("use"))
        # Create the telecom.
        return await Telecom.create(**telecom_data)


class TelecomPatientPeriod(Model):
    id = fields.UUIDField(pk=True)
    telecom = fields.ForeignKeyField("app.Telecom", related_name="telecom_patient_periods")
    patient = fields.ForeignKeyField("app.PatientRecord", related_name="telecom_patient_periods")
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
