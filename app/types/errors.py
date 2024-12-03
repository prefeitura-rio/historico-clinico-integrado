# -*- coding: utf-8 -*-
from pydantic import BaseModel

from app.enums import (
    AcceptTermsEnum
)


class TermAcceptanceErrorModel(BaseModel):
    message: str
    type: AcceptTermsEnum
