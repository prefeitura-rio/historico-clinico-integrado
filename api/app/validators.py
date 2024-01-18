# -*- coding: utf-8 -*-
from tortoise.validators import Validator
from tortoise.exceptions import ValidationError

from validate_docbr import CPF


class CPFValidator(Validator):
    """
    A validator to validate whether the given value is a CPF number or not.
    """
    def __call__(self, value: str):

        is_valid = CPF().validate(value)
        if not is_valid:
            raise ValidationError(f"Value '{value}' is not a CPF")