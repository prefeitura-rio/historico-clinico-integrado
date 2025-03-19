# -*- coding: utf-8 -*-
from enum import Enum


class PermitionEnum(str, Enum):
    HCI_SAME_CPF = "only_from_same_cpf"
    HCI_SAME_HEALTHUNIT = "only_from_same_cnes"
    HCI_SAME_AP = "only_from_same_ap"
    HCI_FULL_PERMITION = "full_permition"


class LoginStatusEnum(str, Enum):
    USER_NOT_FOUND = "user_not_found"       # User don't exist in the DB
    BAD_CREDENTIALS = "bad_credentials"     # User exist but the password is wrong
    REQUIRE_2FA = "require_2fa"             # User exist and the password is correct, but 2FA is required
    BAD_OTP = "bad_otp"                     # User exist and the password is correct, but the OTP is wrong
    INACTIVE_EMPLOYEE = "inactive_employee" # User exist but is not an active employee
    SUCCESS = "success"                     # User exist, password and OTP are correct


class AcceptTermsEnum(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class AccessErrorEnum(str, Enum):
    NOT_FOUND = "NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    DATA_RESTRICTED = "DATA_RESTRICTED"


class SystemEnum(str, Enum):
    VITACARE = "vitacare"
    VITAI = "vitai"
    PRONTUARIO = "prontuario"
    SMSRIO = "smsrio"
    ESUS = "esus"
    MV = "mv"
    WARELINE = "wareline"
    MEDCLINIC = "medclinic"
    SARAH = "sarah"
    NA = "nao se aplica"
    PAPEL = "papel"