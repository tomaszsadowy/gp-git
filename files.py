import os
import hashlib

ZGIT_DIR = ".zgit"


def init():
    os.makedirs(ZGIT_DIR)
    os.makedirs(f"{ZGIT_DIR}/objects")


def hash_object(data, type_="blob"):
    obj = type_.encode() + b"\x00" + data
    obj_id = hashlib.sha1(obj).hexdigest()
    with open(f"{ZGIT_DIR}/objects/{obj_id}", "wb") as out:
        out.write(obj)
    return obj_id


def get_object(obj_id, expected="blob"):
    with open(f"{ZGIT_DIR}/objects/{obj_id}", "rb") as f:
        obj = f.read()

    type_, _, content = obj.partition(b"\x00")
    type_ = type_.decode()

    if expected is not None:
        assert type_ == expected, f"Expected {expected}, got {type_}"
    return content
