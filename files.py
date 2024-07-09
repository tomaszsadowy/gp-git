import os
import hashlib

ZGIT_DIR = '.zgit'

def init():
    os.makedirs(ZGIT_DIR)
    os.makedirs(f'{ZGIT_DIR}/objects')

def hash_object(data):
    obj_id = hashlib.sha1(data).hexdigest()
    with open(f'{ZGIT_DIR}/objects/{obj_id}', 'wb') as out:
        out.write(data)
    return obj_id