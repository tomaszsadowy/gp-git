import os
from . import base
from . import files


REMOTE_REFS_BASE = 'refs/heads/'
LOCAL_REFS_BASE = 'refs/remote/'


def download(remote_path):
    refs = _get_remote_refs(remote_path, REMOTE_REFS_BASE)

    for obj_id in base.iter_objects_in_saves(refs.values ()):
        files.download_object_if_missing(obj_id, remote_path)

    # Update local refs to match server
    for remote_name, value in refs.items():
        refname = os.path.relpath(remote_name, REMOTE_REFS_BASE)
        files.update_ref(f'{LOCAL_REFS_BASE}/{refname}',
                         files.RefValue (symbolic=False, value=value))


def throw(remote_path, refname):
    remote_refs = _get_remote_refs(remote_path)
    remote_ref = remote_refs.get(refname)
    local_ref = files.get_ref(refname).value
   
    assert local_ref
    assert not remote_ref or base.is_ancestor_of(local_ref, remote_ref)

    known_remote_refs = filter(files.object_exists, remote_refs.values())
    remote_objects = set(base.iter_objects_in_saves(known_remote_refs))
    local_objects = set(base.iter_objects_in_saves({local_ref}))
    objects_to_throw = local_objects - remote_objects

    for obj_id in objects_to_throw:
        files.throw_object(obj_id, remote_path)

    with files.change_git_dir(remote_path):
        files.update_ref(refname,
                         files.RefValue (symbolic=False, value=local_ref))


def _get_remote_refs(remote_path, prefix=''):
    with files.change_git_dir(remote_path):
        return {refname: ref.value for refname, ref in files.iter_refs(prefix)}
