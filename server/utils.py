#!/usr/bin/env python

import bcrypt
import hashlib


def pbkdf2_encrypt(password: str, salt: str) -> str:

    return hex(int.from_bytes(hashlib.pbkdf2_hmac("sha3-256", password.encode("utf-8"), salt.encode("utf-8"), 10000, 32), "big"))


def pbkdf2_check(key: str, password: str, salt: str) -> bool:

    if not key.startswith("0x"):
        
        return False

    key = key[2:]

    if len(key) != 64:

        return False

    return int(key, 16) == int.from_bytes(hashlib.pbkdf2_hmac("sha3-256", password.encode("utf-8"), salt.encode("utf-8"), 10000, 32), "big")


def password_hash(password: str, salt: str = "") -> str:

    salted: bytes

    if not salt:

        salted = bcrypt.gensalt()

    else:

        salted = salt.encode("utf-8")

    return bcrypt.hashpw(password.encode("utf-8"), salted).decode("utf-8")


def password_check(password: str, hashed_password: str) -> bool:

    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))