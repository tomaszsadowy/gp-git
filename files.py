import os
import json
import shutil
import hashlib
from collections import namedtuple
from contextlib import contextmanager

GPGIT_DIR = None


@contextmanager
def change_git_dir(new_dir):
    global GPGIT_DIR
    old_dir = GPGIT_DIR
    GPGIT_DIR = f"{new_dir}/.gpgit"
    yield
    GPGIT_DIR = old_dir


def start():
    os.makedirs(GPGIT_DIR)
    os.makedirs(f"{GPGIT_DIR}/objects")


RefValue = namedtuple("RefValue", ["symbolic", "value"])


def update_ref(ref, value, deref=True):
    ref = _get_ref_internal(ref, deref)[0]

    assert value.value
    if value.symbolic:
        value = f"ref: {value.value}"
    else:
        value = value.value

    ref_path = f"{GPGIT_DIR}/{ref}"
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path, "w") as f:
        f.write(value)


def get_ref(ref, deref=True):
    return _get_ref_internal(ref, deref)[1]


def delete_ref(ref, deref=True):
    ref = _get_ref_internal(ref, deref)[0]
    os.remove(f"{GPGIT_DIR}/{ref}")


def _get_ref_internal(ref, deref):
    ref_path = f"{GPGIT_DIR}/{ref}"
    value = None
    if os.path.isfile(ref_path):
        with open(ref_path) as f:
            value = f.read().strip()

    symbolic = bool(value) and value.startswith("ref:")
    if symbolic:
        value = value.split(":", 1)[1].strip()
        if deref:
            return _get_ref_internal(value, deref=True)

    return ref, RefValue(symbolic=False, value=value)


def get_head():
    if os.path.isfile(f"{GPGIT_DIR}/HEAD"):
        with open(f"{GPGIT_DIR}/HEAD") as f:
            return f.read().strip()


def iter_refs(prefix="", deref=True):
    refs = ["HEAD", "COMBINE_HEAD"]
    for root, _, filenames in os.walk(f"{GPGIT_DIR}/refs/"):
        root = os.path.relpath(root, GPGIT_DIR)
        refs.extend(f"{root}/{name}" for name in filenames)

    for refname in refs:
        if not refname.startswith(prefix):
            continue
        ref = get_ref(refname, deref=deref)
        if ref.value:
            yield refname, ref


@contextmanager
def get_index():
    index = {}
    if os.path.isfile(f"{GPGIT_DIR}/index"):
        with open(f"{GPGIT_DIR}/index") as f:
            index = json.load(f)
    yield index

    with open(f"{GPGIT_DIR}/index", "w") as f:
        json.dump(index, f)


def fingerprint(data, type_="blob"):
    obj = type_.encode() + b"\x00" + data
    obj_id = hashlib.sha1(obj).hexdigest()
    with open(f"{GPGIT_DIR}/objects/{obj_id}", "wb") as out:
        out.write(obj)
    return obj_id


def get_object(obj_id, expected="blob"):
    with open(f"{GPGIT_DIR}/objects/{obj_id}", "rb") as f:
        obj = f.read()

    type_, _, content = obj.partition(b"\x00")
    type_ = type_.decode()

    if expected is not None:
        assert type_ == expected, f"Expected {expected}, got {type_}"
    return content


def object_exists(obj_id):
    return os.path.isfile(f"{GPGIT_DIR}/objects/{obj_id}")


def download_object_if_missing(obj_id, remote_git_dir):
    if object_exists(obj_id):
        return
    remote_git_dir += "/.gpgit"
    shutil.copy(f"{remote_git_dir}/objects/{obj_id}", f"{GPGIT_DIR}/objects/{obj_id}")


def throw_object(obj_id, remote_git_dir):
    remote_git_dir += "/.gpgit"
    shutil.copy(f"{GPGIT_DIR}/objects/{obj_id}", f"{remote_git_dir}/objects/{obj_id}")
