# -*- coding: utf-8 -*-
from tortoise import fields
from tortoise.models import Model


class DataSource(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=512)


class RawPatientRecord(Model):
    id          = fields.UUIDField(pk=True)
    data        = fields.JSONField()
    data_source = fields.ForeignKeyField("app.DataSource", related_name="raw_record_data_source")
    created_at  = fields.DatetimeField(auto_now_add=True)
    updated_at  = fields.DatetimeField(auto_now=True)

    class Meta:
        schema="raw"


class RawPatientCondition(Model):
    id          = fields.UUIDField(pk=True)
    data        = fields.JSONField()
    data_source = fields.ForeignKeyField("app.DataSource", related_name="raw_condition_data_source")
    created_at  = fields.DatetimeField(auto_now_add=True)
    updated_at  = fields.DatetimeField(auto_now=True)

    class Meta:
        schema="raw"