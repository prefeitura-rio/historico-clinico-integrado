# -*- coding: utf-8 -*-
from tortoise.validators import Validator
from tortoise.exceptions import ValidationError

from validate_docbr import CPF


class CPFValidator(Validator):
    """
    A validator to validate whether the given value is a CPF number or not.
    """
    def __call__(self, value: str):

        validator = CPF()
        value_digits_str = validator._only_digits(value)

        forbidden_list = [
            '01234567890'
        ]

        if not validator.validate(value_digits_str):
            raise ValidationError(f"Value '{value}' is not a CPF")

        if value_digits_str in forbidden_list:
            raise ValidationError(f"Value '{value}' is forbidden")