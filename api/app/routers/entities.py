# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends
from tortoise.contrib.pydantic import pydantic_model_creator

from app.dependencies import get_current_active_user
from app.models import (
    AddressType,
    AddressUse,
    City,
    Country,
    DataSource,
    Ethnicity,
    Gender,
    Nationality,
    Race,
    State,
    TelecomSystem,
    TelecomUse,
    User,
)

AddressTypeInput = pydantic_model_creator(AddressType, name="AddressTypeInput", exclude=("id",))
AddressTypeOutput = pydantic_model_creator(AddressType, name="AddressTypeOutput")

AddressUseInput = pydantic_model_creator(AddressUse, name="AddressUseInput", exclude=("id",))
AddressUseOutput = pydantic_model_creator(AddressUse, name="AddressUseOutput")

CityInput = pydantic_model_creator(City, name="CityInput", exclude=("id",))
CityOutput = pydantic_model_creator(City, name="CityOutput")

CountryInput = pydantic_model_creator(Country, name="CountryInput", exclude=("id",))
CountryOutput = pydantic_model_creator(Country, name="CountryOutput")

DataSourceInput = pydantic_model_creator(DataSource, name="DataSourceInput", exclude=("id",))
DataSourceOutput = pydantic_model_creator(DataSource, name="DataSourceOutput")

EthnicityInput = pydantic_model_creator(Ethnicity, name="EthnicityInput", exclude=("id",))
EthnicityOutput = pydantic_model_creator(Ethnicity, name="EthnicityOutput")

GenderInput = pydantic_model_creator(Gender, name="GenderInput", exclude=("id",))
GenderOutput = pydantic_model_creator(Gender, name="GenderOutput")

NationalityInput = pydantic_model_creator(Nationality, name="NationalityInput", exclude=("id",))
NationalityOutput = pydantic_model_creator(Nationality, name="NationalityOutput")

RaceInput = pydantic_model_creator(Race, name="RaceInput", exclude=("id",))
RaceOutput = pydantic_model_creator(Race, name="RaceOutput")

StateInput = pydantic_model_creator(State, name="StateInput", exclude=("id",))
StateOutput = pydantic_model_creator(State, name="StateOutput")

TelecomSystemInput = pydantic_model_creator(
    TelecomSystem, name="TelecomSystemInput", exclude=("id",)
)
TelecomSystemOutput = pydantic_model_creator(TelecomSystem, name="TelecomSystemOutput")

TelecomUseInput = pydantic_model_creator(TelecomUse, name="TelecomUseInput", exclude=("id",))
TelecomUseOutput = pydantic_model_creator(TelecomUse, name="TelecomUseOutput")

router = APIRouter(prefix="/entities", tags=["entities"])


@router.get("/address_type", response_model=list[AddressTypeOutput])
async def get_address_types(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[AddressTypeOutput]:
    return await AddressTypeOutput.from_queryset(AddressType.all())


@router.post("/address_type", response_model=AddressTypeOutput, status_code=201)
async def create_address_type(
    _: Annotated[User, Depends(get_current_active_user)],
    address_type_input: AddressTypeInput,
) -> AddressTypeOutput:
    address_type = await AddressType.create(**address_type_input.dict(exclude_unset=True))
    return await AddressTypeOutput.from_tortoise_orm(address_type)


@router.patch("/address_type/{address_type_id}", response_model=AddressTypeOutput)
async def update_address_type(
    _: Annotated[User, Depends(get_current_active_user)],
    address_type_id: int,
    address_type_input: AddressTypeInput,
) -> AddressTypeOutput:
    await AddressType.filter(id=address_type_id).update(
        **address_type_input.dict(exclude_unset=True)
    )
    return await AddressTypeOutput.from_queryset_single(AddressType.get(id=address_type_id))


@router.delete("/address_type/{address_type_id}", response_model=dict[str, bool])
async def delete_address_type(
    _: Annotated[User, Depends(get_current_active_user)],
    address_type_id: int,
) -> dict[str, bool]:
    deleted_count = await AddressType.filter(id=address_type_id).delete()
    return {"deleted": deleted_count == 1}


@router.get("/address_use", response_model=list[AddressUseOutput])
async def get_address_uses(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[AddressUseOutput]:
    return await AddressUseOutput.from_queryset(AddressUse.all())


@router.post("/address_use", response_model=AddressUseOutput, status_code=201)
async def create_address_use(
    _: Annotated[User, Depends(get_current_active_user)],
    address_use_input: AddressUseInput,
) -> AddressUseOutput:
    address_use = await AddressUse.create(**address_use_input.dict(exclude_unset=True))
    return await AddressUseOutput.from_tortoise_orm(address_use)


@router.patch("/address_use/{address_use_id}", response_model=AddressUseOutput)
async def update_address_use(
    _: Annotated[User, Depends(get_current_active_user)],
    address_use_id: int,
    address_use_input: AddressUseInput,
) -> AddressUseOutput:
    await AddressUse.filter(id=address_use_id).update(**address_use_input.dict(exclude_unset=True))
    return await AddressUseOutput.from_queryset_single(AddressUse.get(id=address_use_id))


@router.delete("/address_use/{address_use_id}", response_model=dict[str, bool])
async def delete_address_use(
    _: Annotated[User, Depends(get_current_active_user)],
    address_use_id: int,
) -> dict[str, bool]:
    deleted_count = await AddressUse.filter(id=address_use_id).delete()
    return {"deleted": deleted_count == 1}


@router.get("/city", response_model=list[CityOutput])
async def get_cities(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[CityOutput]:
    return await CityOutput.from_queryset(City.all())


@router.post("/city", response_model=CityOutput, status_code=201)
async def create_city(
    _: Annotated[User, Depends(get_current_active_user)],
    city_input: CityInput,
) -> CityOutput:
    city = await City.create(**city_input.dict(exclude_unset=True))
    return await CityOutput.from_tortoise_orm(city)


@router.patch("/city/{city_id}", response_model=CityOutput)
async def update_city(
    _: Annotated[User, Depends(get_current_active_user)],
    city_id: int,
    city_input: CityInput,
) -> CityOutput:
    await City.filter(id=city_id).update(**city_input.dict(exclude_unset=True))
    return await CityOutput.from_queryset_single(City.get(id=city_id))


@router.delete("/city/{city_id}", response_model=dict[str, bool])
async def delete_city(
    _: Annotated[User, Depends(get_current_active_user)],
    city_id: int,
) -> dict[str, bool]:
    deleted_count = await City.filter(id=city_id).delete()
    return {"deleted": deleted_count == 1}


@router.get("/country", response_model=list[CountryOutput])
async def get_countries(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[CountryOutput]:
    return await CountryOutput.from_queryset(Country.all())


@router.post("/country", response_model=CountryOutput, status_code=201)
async def create_country(
    _: Annotated[User, Depends(get_current_active_user)],
    country_input: CountryInput,
) -> CountryOutput:
    country = await Country.create(**country_input.dict(exclude_unset=True))
    return await CountryOutput.from_tortoise_orm(country)


@router.patch("/country/{country_id}", response_model=CountryOutput)
async def update_country(
    _: Annotated[User, Depends(get_current_active_user)],
    country_id: int,
    country_input: CountryInput,
) -> CountryOutput:
    await Country.filter(id=country_id).update(**country_input.dict(exclude_unset=True))
    return await CountryOutput.from_queryset_single(Country.get(id=country_id))


@router.delete("/country/{country_id}", response_model=dict[str, bool])
async def delete_country(
    _: Annotated[User, Depends(get_current_active_user)],
    country_id: int,
) -> dict[str, bool]:
    deleted_count = await Country.filter(id=country_id).delete()
    return {"deleted": deleted_count == 1}


@router.get("/data_source", response_model=list[DataSourceOutput])
async def get_data_sources(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[DataSourceOutput]:
    return await DataSourceOutput.from_queryset(DataSource.all())


@router.post("/data_source", response_model=DataSourceOutput, status_code=201)
async def create_data_source(
    _: Annotated[User, Depends(get_current_active_user)],
    data_source_input: DataSourceInput,
) -> DataSourceOutput:
    data_source = await DataSource.create(**data_source_input.dict(exclude_unset=True))
    return await DataSourceOutput.from_tortoise_orm(data_source)


@router.patch("/data_source/{data_source_id}", response_model=DataSourceOutput)
async def update_data_source(
    _: Annotated[User, Depends(get_current_active_user)],
    data_source_id: int,
    data_source_input: DataSourceInput,
) -> DataSourceOutput:
    await DataSource.filter(id=data_source_id).update(**data_source_input.dict(exclude_unset=True))
    return await DataSourceOutput.from_queryset_single(DataSource.get(id=data_source_id))


@router.delete("/data_source/{data_source_id}", response_model=dict[str, bool])
async def delete_data_source(
    _: Annotated[User, Depends(get_current_active_user)],
    data_source_id: int,
) -> dict[str, bool]:
    deleted_count = await DataSource.filter(id=data_source_id).delete()
    return {"deleted": deleted_count == 1}


@router.get("/ethnicity", response_model=list[EthnicityOutput])
async def get_ethnicities(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[EthnicityOutput]:
    return await EthnicityOutput.from_queryset(Ethnicity.all())


@router.post("/ethnicity", response_model=EthnicityOutput, status_code=201)
async def create_ethnicity(
    _: Annotated[User, Depends(get_current_active_user)],
    ethnicity_input: EthnicityInput,
) -> EthnicityOutput:
    ethnicity = await Ethnicity.create(**ethnicity_input.dict(exclude_unset=True))
    return await EthnicityOutput.from_tortoise_orm(ethnicity)


@router.patch("/ethnicity/{ethnicity_id}", response_model=EthnicityOutput)
async def update_ethnicity(
    _: Annotated[User, Depends(get_current_active_user)],
    ethnicity_id: int,
    ethnicity_input: EthnicityInput,
) -> EthnicityOutput:
    await Ethnicity.filter(id=ethnicity_id).update(**ethnicity_input.dict(exclude_unset=True))
    return await EthnicityOutput.from_queryset_single(Ethnicity.get(id=ethnicity_id))


@router.delete("/ethnicity/{ethnicity_id}", response_model=dict[str, bool])
async def delete_ethnicity(
    _: Annotated[User, Depends(get_current_active_user)],
    ethnicity_id: int,
) -> dict[str, bool]:
    deleted_count = await Ethnicity.filter(id=ethnicity_id).delete()
    return {"deleted": deleted_count == 1}


@router.get("/gender", response_model=list[GenderOutput])
async def get_genders(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[GenderOutput]:
    return await GenderOutput.from_queryset(Gender.all())


@router.post("/gender", response_model=GenderOutput, status_code=201)
async def create_gender(
    _: Annotated[User, Depends(get_current_active_user)],
    gender_input: GenderInput,
) -> GenderOutput:
    gender = await Gender.create(**gender_input.dict(exclude_unset=True))
    return await GenderOutput.from_tortoise_orm(gender)


@router.patch("/gender/{gender_id}", response_model=GenderOutput)
async def update_gender(
    _: Annotated[User, Depends(get_current_active_user)],
    gender_id: int,
    gender_input: GenderInput,
) -> GenderOutput:
    await Gender.filter(id=gender_id).update(**gender_input.dict(exclude_unset=True))
    return await GenderOutput.from_queryset_single(Gender.get(id=gender_id))


@router.delete("/gender/{gender_id}", response_model=dict[str, bool])
async def delete_gender(
    _: Annotated[User, Depends(get_current_active_user)],
    gender_id: int,
) -> dict[str, bool]:
    deleted_count = await Gender.filter(id=gender_id).delete()
    return {"deleted": deleted_count == 1}


@router.get("/nationality", response_model=list[NationalityOutput])
async def get_nationalities(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[NationalityOutput]:
    return await NationalityOutput.from_queryset(Nationality.all())


@router.post("/nationality", response_model=NationalityOutput, status_code=201)
async def create_nationality(
    _: Annotated[User, Depends(get_current_active_user)],
    nationality_input: NationalityInput,
) -> NationalityOutput:
    nationality = await Nationality.create(**nationality_input.dict(exclude_unset=True))
    return await NationalityOutput.from_tortoise_orm(nationality)


@router.patch("/nationality/{nationality_id}", response_model=NationalityOutput)
async def update_nationality(
    _: Annotated[User, Depends(get_current_active_user)],
    nationality_id: int,
    nationality_input: NationalityInput,
) -> NationalityOutput:
    await Nationality.filter(id=nationality_id).update(**nationality_input.dict(exclude_unset=True))
    return await NationalityOutput.from_queryset_single(Nationality.get(id=nationality_id))


@router.delete("/nationality/{nationality_id}", response_model=dict[str, bool])
async def delete_nationality(
    _: Annotated[User, Depends(get_current_active_user)],
    nationality_id: int,
) -> dict[str, bool]:
    deleted_count = await Nationality.filter(id=nationality_id).delete()
    return {"deleted": deleted_count == 1}


@router.get("/race", response_model=list[RaceOutput])
async def get_races(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[RaceOutput]:
    return await RaceOutput.from_queryset(Race.all())


@router.post("/race", response_model=RaceOutput, status_code=201)
async def create_race(
    _: Annotated[User, Depends(get_current_active_user)],
    race_input: RaceInput,
) -> RaceOutput:
    race = await Race.create(**race_input.dict(exclude_unset=True))
    return await RaceOutput.from_tortoise_orm(race)


@router.patch("/race/{race_id}", response_model=RaceOutput)
async def update_race(
    _: Annotated[User, Depends(get_current_active_user)],
    race_id: int,
    race_input: RaceInput,
) -> RaceOutput:
    await Race.filter(id=race_id).update(**race_input.dict(exclude_unset=True))
    return await RaceOutput.from_queryset_single(Race.get(id=race_id))


@router.delete("/race/{race_id}", response_model=dict[str, bool])
async def delete_race(
    _: Annotated[User, Depends(get_current_active_user)],
    race_id: int,
) -> dict[str, bool]:
    deleted_count = await Race.filter(id=race_id).delete()
    return {"deleted": deleted_count == 1}


@router.get("/state", response_model=list[StateOutput])
async def get_states(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[StateOutput]:
    return await StateOutput.from_queryset(State.all())


@router.post("/state", response_model=StateOutput, status_code=201)
async def create_state(
    _: Annotated[User, Depends(get_current_active_user)],
    state_input: StateInput,
) -> StateOutput:
    state = await State.create(**state_input.dict(exclude_unset=True))
    return await StateOutput.from_tortoise_orm(state)


@router.patch("/state/{state_id}", response_model=StateOutput)
async def update_state(
    _: Annotated[User, Depends(get_current_active_user)],
    state_id: int,
    state_input: StateInput,
) -> StateOutput:
    await State.filter(id=state_id).update(**state_input.dict(exclude_unset=True))
    return await StateOutput.from_queryset_single(State.get(id=state_id))


@router.delete("/state/{state_id}", response_model=dict[str, bool])
async def delete_state(
    _: Annotated[User, Depends(get_current_active_user)],
    state_id: int,
) -> dict[str, bool]:
    deleted_count = await State.filter(id=state_id).delete()
    return {"deleted": deleted_count == 1}


@router.get("/telecom_system", response_model=list[TelecomSystemOutput])
async def get_telecom_systems(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[TelecomSystemOutput]:
    return await TelecomSystemOutput.from_queryset(TelecomSystem.all())


@router.post("/telecom_system", response_model=TelecomSystemOutput, status_code=201)
async def create_telecom_system(
    _: Annotated[User, Depends(get_current_active_user)],
    telecom_system_input: TelecomSystemInput,
) -> TelecomSystemOutput:
    telecom_system = await TelecomSystem.create(**telecom_system_input.dict(exclude_unset=True))
    return await TelecomSystemOutput.from_tortoise_orm(telecom_system)


@router.patch("/telecom_system/{telecom_system_id}", response_model=TelecomSystemOutput)
async def update_telecom_system(
    _: Annotated[User, Depends(get_current_active_user)],
    telecom_system_id: int,
    telecom_system_input: TelecomSystemInput,
) -> TelecomSystemOutput:
    await TelecomSystem.filter(id=telecom_system_id).update(
        **telecom_system_input.dict(exclude_unset=True)
    )
    return await TelecomSystemOutput.from_queryset_single(TelecomSystem.get(id=telecom_system_id))


@router.delete("/telecom_system/{telecom_system_id}", response_model=dict[str, bool])
async def delete_telecom_system(
    _: Annotated[User, Depends(get_current_active_user)],
    telecom_system_id: int,
) -> dict[str, bool]:
    deleted_count = await TelecomSystem.filter(id=telecom_system_id).delete()
    return {"deleted": deleted_count == 1}


@router.get("/telecom_use", response_model=list[TelecomUseOutput])
async def get_telecom_uses(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[TelecomUseOutput]:
    return await TelecomUseOutput.from_queryset(TelecomUse.all())


@router.post("/telecom_use", response_model=TelecomUseOutput, status_code=201)
async def create_telecom_use(
    _: Annotated[User, Depends(get_current_active_user)],
    telecom_use_input: TelecomUseInput,
) -> TelecomUseOutput:
    telecom_use = await TelecomUse.create(**telecom_use_input.dict(exclude_unset=True))
    return await TelecomUseOutput.from_tortoise_orm(telecom_use)


@router.patch("/telecom_use/{telecom_use_id}", response_model=TelecomUseOutput)
async def update_telecom_use(
    _: Annotated[User, Depends(get_current_active_user)],
    telecom_use_id: int,
    telecom_use_input: TelecomUseInput,
) -> TelecomUseOutput:
    await TelecomUse.filter(id=telecom_use_id).update(**telecom_use_input.dict(exclude_unset=True))
    return await TelecomUseOutput.from_queryset_single(TelecomUse.get(id=telecom_use_id))


@router.delete("/telecom_use/{telecom_use_id}", response_model=dict[str, bool])
async def delete_telecom_use(
    _: Annotated[User, Depends(get_current_active_user)],
    telecom_use_id: int,
) -> dict[str, bool]:
    deleted_count = await TelecomUse.filter(id=telecom_use_id).delete()
    return {"deleted": deleted_count == 1}
