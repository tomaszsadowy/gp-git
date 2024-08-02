import itertools
import operator
import os
import string
from collections import deque, namedtuple
import files
import compare


def start():
    files.start()
    files.update_ref("HEAD", files.RefValue(symbolic=True, value="refs/heads/master"))


def write_tree():
    index_as_tree = {}
    with files.get_index() as index:
        for path, obj_id in index.items():
            path = path.split("/")
            dirpath, filename = path[:-1], path[-1]

            current = index_as_tree
            for dirname in dirpath:
                current = current.setdefault(dirname, {})
            current[filename] = obj_id

    def write_tree_recursive(tree_dict):
        entries = []
        for name, value in tree_dict.items():
            if type(value) is dict:
                type_ = "tree"
                obj_id = write_tree_recursive(value)
            else:
                type_ = "blob"
                obj_id = value
            entries.append((name, obj_id, type_))

        tree = "".join(
            f"{type_} {obj_id} {name}\n" for name, obj_id, type_ in sorted(entries)
        )
        return files.fingerprint(tree.encode(), "tree")

    return write_tree_recursive(index_as_tree)


def _iter_tree_entries(obj_id):
    if not obj_id:
        return
    tree = files.get_object(obj_id, "tree")
    for entry in tree.decode().splitlines():
        type_, obj_id, name = entry.split(" ", 2)
        yield type_, obj_id, name


def get_tree(obj_id, base_path=""):
    result = {}
    for type_, obj_id, name in _iter_tree_entries(obj_id):
        assert "/" not in name
        assert name not in ("..", ".")
        path = base_path + name
        if type_ == "blob":
            result[path] = obj_id
        elif type_ == "tree":
            result.update(get_tree(obj_id, f"{path}/"))
        else:
            assert False, f"Unknown tree entry {type_}"
    return result


def get_working_tree():
    result = {}
    for root, _, filenames in os.walk("."):
        for filename in filenames:
            path = os.path.relpath(f"{root}/{filename}")
            if is_ignored(path) or not os.path.isfile(path):
                continue
            with open(path, "rb") as f:
                result[path] = files.fingerprint(f.read())
        return result


def get_index_tree():
    with files.get_index() as index:
        return index


def _empty_current_directory():
    for root, dirnames, filenames in os.walk(".", topdown=False):
        for filename in filenames:
            path = os.path.relpath(f"{root}/{filename}")
            if is_ignored(path) or not os.path.isfile(path):
                continue
            os.remove(path)
        for dirname in dirnames:
            path = os.path.relpath(f"{root}/{dirname}")
            if is_ignored(path):
                continue
            try:
                os.rmdir(path)
            except OSError:
                pass


def read_tree(tree_obj_id, update_working=False):
    with files.get_index() as index:
        index.clear()
        index.update(get_tree(tree_obj_id))

        if update_working:
            _switch_index(index)


def read_tree_combined(t_base, t_HEAD, t_other, update_working=False):
    with files.get_index() as index:
        index.clear()
        index.update(
            compare.combine_trees(get_tree(t_base), get_tree(t_HEAD), get_tree(t_other))
        )

        if update_working:
            _switch_index(index)


def _switch_index(index):
    _empty_current_directory()
    for path, obj_id in index.items():
        os.makedirs(os.path.dirname(f"./{path}"), exist_ok=True)
        with open(path, "wb") as f:
            f.write(files.get_object(obj_id, "blob"))


def save(message):
    save = f"tree {write_tree()}\n"
    HEAD = files.get_ref("HEAD").value
    if HEAD:
        save += f"parent {HEAD}\n"
    COMBINE_HEAD = files.get_ref("COMBINE_HEAD").value
    if COMBINE_HEAD:
        save += f"parent {COMBINE_HEAD}\n"
        files.delete_ref("COMBINE_HEAD", deref=False)

    save += "\n"
    save += f"{message}\n"

    obj_id = files.fingerprint(save.encode(), "save")
    files.update_ref("HEAD", files.RefValue(symbolic=False, value=obj_id))
    return obj_id


def switch(name):
    obj_id = get_obj_id(name)
    save = get_save(obj_id)
    read_tree(save.tree, update_working=True)

    if is_branch(name):
        HEAD = files.RefValue(symbolic=True, value=f"refs/heads/{name}")
    else:
        HEAD = files.RefValue(symbolic=False, value=obj_id)

    files.update_ref("HEAD", HEAD, deref=False)


def reset(obj_id):
    files.update_ref("HEAD", files.RefValue(symbolic=False, value=obj_id))


def combine(other):
    HEAD = files.get_ref("HEAD").value
    assert HEAD
    combine_base = get_combine_base(other, HEAD)
    c_other = get_save(other)

    if combine_base == HEAD:
        read_tree(c_other.tree, update_working=True)
        files.update_ref("HEAD", files.RefValue(symbolic=False, value=other))
        print("Fast-forward combine, no need to save")
        return

    files.update_ref("COMBINE_HEAD", files.RefValue(symbolic=False, value=other))

    c_base = get_save(combine_base)
    c_HEAD = get_save(HEAD)
    read_tree_combined(c_base.tree, c_HEAD.tree, c_other.tree, update_working=True)
    print("Combined in working tree\nPlease save")


def get_combine_base(obj_id1, obj_id2):
    parents1 = set(iter_saves_and_parents({obj_id1}))

    for obj_id in iter_saves_and_parents({obj_id2}):
        if obj_id in parents1:
            return obj_id


def is_ancestor_of(save, maybe_ancestor):
    return maybe_ancestor in iter_saves_and_parents({save})


def create_label(name, obj_id):
    files.update_ref(f"refs/labels/{name}", files.RefValue(symbolic=False, value=obj_id))


def iter_branch_names():
    for refname, _ in files.iter_refs("refs/heads/"):
        yield os.path.relpath(refname, "refs/heads/")


def is_branch(branch):
    return files.get_ref(f"refs/heads/{branch}").value is not None


def get_branch_name():
    HEAD = files.get_ref("HEAD", deref=False)
    if not HEAD.symbolic:
        return None
    HEAD = HEAD.value
    assert HEAD.startswith("refs/heads/")
    return os.path.relpath(HEAD, "refs/heads")


def create_branch(name, obj_id):
    files.update_ref(f"refs/heads/{name}", files.RefValue(symbolic=False, value=obj_id))


_save = namedtuple("_save", ["tree", "parents", "message"])


def get_save(obj_id):
    parents = []

    save = files.get_object(obj_id, "save").decode()
    lines = iter(save.splitlines())
    for line in itertools.takewhile(operator.truth, lines):
        key, value = line.split(" ", 1)
        if key == "tree":
            tree = value
        elif key == "parent":
            parents.append(value)
        else:
            assert False, f"Unknown field {key}"

    message = "\n".join(lines)
    return _save(tree=tree, parents=parents, message=message)


def iter_saves_and_parents(obj_ids):
    obj_ids = deque(obj_ids)
    visited = set()

    while obj_ids:
        obj_id = obj_ids.popleft()
        if not obj_id or obj_id in visited:
            continue
        visited.add(obj_id)
        yield obj_id

        save = get_save(obj_id)
        obj_ids.extendleft(save.parents[:1])
        obj_ids.extend(save.parents[1:])


def iter_objects_in_saves(obj_ids):
    visited = set()

    def iter_objects_in_tree(obj_id):
        visited.add(obj_id)
        yield obj_id
        for type_, obj_id, _ in _iter_tree_entries(obj_id):
            if obj_id not in visited:
                if type_ == "tree":
                    yield from iter_objects_in_tree(obj_id)
                else:
                    visited.add(obj_id)
                    yield obj_id

    for obj_id in iter_saves_and_parents(obj_ids):
        yield obj_id
        save = get_save(obj_id)
        if save.tree not in visited:
            yield from iter_objects_in_tree(save.tree)


def get_obj_id(name):
    if name == "@":
        name = "HEAD"

    refs_to_try = [
        f"{name}",
        f"refs/{name}",
        f"refs/labels/{name}",
        f"refs/heads/{name}",
    ]
    for ref in refs_to_try:
        if files.get_ref(ref).value():
            return files.get_ref(ref).value

    # Name is SHA1
    is_hex = all(c in string.hexdigits for c in name)
    if len(name) == 40 and is_hex:
        return name

    assert False, f"Unknown name {name}"


def track(filenames):

    def track_file(filename):
        filename = os.path.relpath(filename)
        with open(filename, "rb") as f:
            obj_id = files.fingerprint(f.read())
        index[filename] = obj_id

    def track_directory(dirname):
        for root, _, filenames in os.walk(dirname):
            for filename in filenames:
                path = os.path.relpath(f"{root}/{filename}")
                if is_ignored(path) or not os.path.isfile(path):
                    continue
                track_file(path)

    with files.get_index() as index:
        for name in filenames:
            if os.path.isfile(name):
                track_file(name)
            elif os.path.isdir(name):
                track_directory(name)


def is_ignored(path):
    return ".gpgit" in path.split("/")
