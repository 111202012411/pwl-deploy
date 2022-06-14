#!/usr/bin/env python

from typing import List, Optional, Tuple, Union
from pydantic import BaseModel

class UserSchema(BaseModel):

    id: Optional[int]
    username: str
    name: str
    photo: Optional[str]
    password: Optional[str]
    gender: str
    day_of_birthday: str
    email: str
    email_verify: Optional[bool]
    phone: str
    phone_verify: Optional[bool]
    address: str
    country: str
    language: str
    pos_code: str
    verify: Optional[bool]
    admin: Optional[bool]
    created: Optional[int]
    modified: Optional[int]


class ProductSchema(BaseModel):

    id: Optional[int]
    name: str
    photo: Optional[str]
    description: str
    categories: Union[Tuple[str], List[str], str]
    period_of_time: str
    license: Optional[str]
    author: str
    vendor: Optional[str]
    price: int
    sale: Optional[int]
    created: Optional[int]
    modified: Optional[int]


class TransactionSchema(BaseModel):

    id: Optional[int]
    user_id: int
    product_id: int
    payment_type: str
    payment_paid: Optional[bool]
    activate: Optional[bool]
    expired: Optional[int]
    created: Optional[int]
    modified: Optional[int]
