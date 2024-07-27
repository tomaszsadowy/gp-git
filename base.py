import os
import files

def write_tree(directory='.'):
    entries = []
    with os.scandir(directory) as it:
        for entry in it:
            full = f'{directory}/{entry.name}'
            if is_ignored(full):
                continue
            if entry.is_file(follow_symlinks=False):
                type_ = 'blob'
                with open(full, 'rb') as f:
                    obj_id = files.hash_object(f.read())
            elif entry.is_dir(follow_symlinks=False):
                type_ = 'tree'
                obj_id = write_tree(full)
            entries.append((entry.name, obj_id, type_))
    
    tree = ''.join(f'{type_} {obj_id} {name}\n'
                   for name, obj_id, type_
                   in sorted(entries))
    return files.hash_object(tree.encode(), 'tree')

def _iter_tree_entries (obj_id):
    if not obj_id:
        return
    tree = files.get_object (obj_id, 'tree')
    for entry in tree.decode ().splitlines ():
        type_, obj_id, name = entry.split (' ', 2)
        yield type_, obj_id, name


def get_tree (obj_id, base_path=''):
    result = {}
    for type_, obj_id, name in _iter_tree_entries (obj_id):
        assert '/' not in name
        assert name not in ('..', '.')
        path = base_path + name
        if type_ == 'blob':
            result[path] = obj_id
        elif type_ == 'tree':
            result.update (get_tree (obj_id, f'{path}/'))
        else:
            assert False, f'Unknown tree entry {type_}'
    return result


def read_tree (tree_obj_id):
    for path, obj_id in get_tree (tree_obj_id, base_path='./').items ():
        os.makedirs (os.path.dirname (path), exist_ok=True)
        with open (path, 'wb') as f:
            f.write (files.get_object (obj_id))

def is_ignored(path):
    return '.zgit' in path.split('/')