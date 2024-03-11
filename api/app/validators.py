# -*- coding: utf-8 -*-
import datetime
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


class PatientCodeValidator(CPFValidator):
    """
    A validator to validate whether the given value is a CPF number or not.
    """
    def __call__(self, value: str):

        parts = value.split(".")

        if len(parts) != 2:
            raise ValidationError(f"Value '{value}' is not a valid patient code")

        cpf, birth_date = parts

        # Part 1 - Validate CPF
        super().__call__(cpf)

        # Part 2 - Validate Birth Date
        if len(birth_date) != 8:
            raise ValidationError(f"Value '{value}' is not a valid patient code")

        birth_date_as_date = datetime.datetime.strptime(birth_date, '%Y%m%d')

        if birth_date_as_date > datetime.datetime.now():
            raise ValidationError(f"Value '{value}' is not a valid patient code")