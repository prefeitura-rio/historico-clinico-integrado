# -*- coding: utf-8 -*-
from tortoise import fields
from tortoise.models import Model

from app.enums import (
    PermitionEnum,
)
from app.validators import CPFValidator


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    name = fields.CharField(max_length=255, null=True)
    cpf = fields.CharField(max_length=11, unique=True, null=True, validators=[CPFValidator()])
    access_level = fields.CharEnumField(PermitionEnum, index=True, max_length=50, null=True)
    job_title = fields.CharField(max_length=255, null=True)
    cnes = fields.CharField(max_length=50, null=True)
    ap = fields.CharField(max_length=2, null=True)
    is_use_terms_accepted = fields.BooleanField(default=False)
    use_terms_accepted_at = fields.DatetimeField(null=True)
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
