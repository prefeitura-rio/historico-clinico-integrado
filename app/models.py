# -*- coding: utf-8 -*-
from tortoise import fields
from tortoise.models import Model

from app.enums import (
    SystemEnum,
    PermitionEnum
)
from app.validators import CPFValidator


class DataSource(Model):
    cnes = fields.CharField(max_length=50, unique=True, pk=True)
    ap = fields.CharField(max_length=2, null=True)
    system = fields.CharEnumField(SystemEnum, index=True, max_length=50, null=True)
    description = fields.CharField(max_length=512, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class TableInitialization(Model):
    id = fields.IntField(pk=True)
    table_name = fields.CharField(max_length=255, unique=True)
    last_version = fields.IntField(null=True)

    class Meta:
        table = "meta__tableinitialization"


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    name = fields.CharField(max_length=255, null=True)
    cpf = fields.CharField(max_length=11, unique=True, null=True, validators=[CPFValidator()])
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255)
    data_source = fields.ForeignKeyField("app.DataSource", related_name="users", null=True)
    role = fields.ForeignKeyField("app.SystemRole", related_name="user_role", null=True)
    # 2FA
    secret_key = fields.CharField(max_length=255, null=True)
    is_2fa_required = fields.BooleanField(default=False)
    is_2fa_activated = fields.BooleanField(default=False)
    # Metadata
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


class SystemRole(Model):
    # Information
    slug = fields.CharField(pk=True, max_length=255, unique=True)
    job_title = fields.CharField(max_length=255, null=True)
    role_title = fields.CharField(max_length=255, null=True)
    permition = fields.ForeignKeyField("app.Permition", related_name="role_permition", null=True)
    # Metadata
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class Permition(Model):
    #Information
    slug = fields.CharEnumField(pk=True, enum_type=PermitionEnum, default=PermitionEnum.HCI_SAME_CPF)
    description = fields.CharField(max_length=255)
    filter_clause = fields.CharField(max_length=255, null=False)
    # Metadata
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
