# -*- coding: utf-8 -*-
from enum import Enum


class LoginStatusEnum(str, Enum):
    USER_NOT_FOUND = "user_not_found"       # User don't exist in the DB
    BAD_CREDENTIALS = "bad_credentials"     # User exist but the password is wrong
    REQUIRE_2FA = "require_2fa"             # User exist and the password is correct, but 2FA is required
    BAD_OTP = "bad_otp"                     # User exist and the password is correct, but the OTP is wrong
    INACTIVE_EMPLOYEE = "inactive_employee" # User exist but is not an active employee
    SUCCESS = "success"                     # User exist, password and OTP are correct
    EMAIL_QUEUE_ERROR = "email_queue_error" # User exist, error in email queueing
    EMAIL_ANONYMIZATION_ERROR = "email_anonymization_error"  # User exist, error in email anonymization