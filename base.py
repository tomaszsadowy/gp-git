import itertools
import operator
import os
import string
from collections import deque, namedtuple
import files
import diff


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
        return files.hash_object(tree.encode(), "tree")

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
                result[path] = files.hash_object(f.read())
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
            _checkout_index(index)


def read_tree_merged(t_base, t_HEAD, t_other, update_working=False):
    with files.get_index() as index:
        index.clear()
        index.update(
            diff.merge_trees(get_tree(t_base), get_tree(t_HEAD), get_tree(t_other))
        )

        if update_working:
            _checkout_index(index)


def _checkout_index(index):
    _empty_current_directory()
    for path, obj_id in index.items():
        os.makedirs(os.path.dirname(f"./{path}"), exist_ok=True)
        with open(path, "wb") as f:
            f.write(files.get_object(obj_id, "blob"))


def commit(message):
    commit = f"tree {write_tree()}\n"
    HEAD = files.get_ref("HEAD").value
    if HEAD:
        commit += f"parent {HEAD}\n"
    MERGE_HEAD = files.get_ref("MERGE_HEAD").value
    if MERGE_HEAD:
        commit += f"parent {MERGE_HEAD}\n"
        files.delete_ref("MERGE_HEAD", deref=False)

    commit += "\n"
    commit += f"{message}\n"

    obj_id = files.hash_object(commit.encode(), "commit")
    files.update_ref("HEAD", files.RefValue(symbolic=False, value=obj_id))
    return obj_id


def checkout(name):
    obj_id = get_obj_id(name)
    commit = get_commit(obj_id)
    read_tree(commit.tree, update_working=True)

    if is_branch(name):
        HEAD = files.RefValue(symbolic=True, value=f"refs/heads/{name}")
    else:
        HEAD = files.RefValue(symbolic=False, value=obj_id)

    files.update_ref("HEAD", HEAD, deref=False)


def reset(obj_id):
    files.update_ref("HEAD", files.RefValue(symbolic=False, value=obj_id))


def merge(other):
    HEAD = files.get_ref("HEAD").value
    assert HEAD
    merge_base = get_merge_base(other, HEAD)
    c_other = get_commit(other)

    if merge_base == HEAD:
        read_tree(c_other.tree, update_working=True)
        files.update_ref("HEAD", files.RefValue(symbolic=False, value=other))
        print("Fast-forward merge, no need to commit")
        return

    files.update_ref("MERGE_HEAD", files.RefValue(symbolic=False, value=other))

    c_base = get_commit(merge_base)
    c_HEAD = get_commit(HEAD)
    read_tree_merged(c_base.tree, c_HEAD.tree, c_other.tree, update_working=True)
    print("Merged in working tree\nPlease commit")


def get_merge_base(obj_id1, obj_id2):
    parents1 = set(iter_commits_and_parents({obj_id1}))

    for obj_id in iter_commits_and_parents({obj_id2}):
        if obj_id in parents1:
            return obj_id


def is_ancestor_of(commit, maybe_ancestor):
    return maybe_ancestor in iter_commits_and_parents({commit})


def create_tag(name, obj_id):
    files.update_ref(f"refs/tags/{name}", files.RefValue(symbolic=False, value=obj_id))


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


_commit = namedtuple("_commit", ["tree", "parents", "message"])


def get_commit(obj_id):
    parents = []

    commit = files.get_object(obj_id, "commit").decode()
    lines = iter(commit.splitlines())
    for line in itertools.takewhile(operator.truth, lines):
        key, value = line.split(" ", 1)
        if key == "tree":
            tree = value
        elif key == "parent":
            parents.append(value)
        else:
            assert False, f"Unknown field {key}"

    message = "\n".join(lines)
    return _commit(tree=tree, parents=parents, message=message)


def iter_commits_and_parents(obj_ids):
    obj_ids = deque(obj_ids)
    visited = set()

    while obj_ids:
        obj_id = obj_ids.popleft()
        if not obj_id or obj_id in visited:
            continue
        visited.add(obj_id)
        yield obj_id

        commit = get_commit(obj_id)
        obj_ids.extendleft(commit.parents[:1])
        obj_ids.extend(commit.parents[1:])


def iter_objects_in_commits(obj_ids):
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

    for obj_id in iter_commits_and_parents(obj_ids):
        yield obj_id
        commit = get_commit(obj_id)
        if commit.tree not in visited:
            yield from iter_objects_in_tree(commit.tree)


def get_obj_id(name):
    if name == "@":
        name = "HEAD"

    refs_to_try = [
        f"{name}",
        f"refs/{name}",
        f"refs/tags/{name}",
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


def add(filenames):

    def add_file(filename):
        filename = os.path.relpath(filename)
        with open(filename, "rb") as f:
            obj_id = files.hash_object(f.read())
        index[filename] = obj_id

    def add_directory(dirname):
        for root, _, filenames in os.walk(dirname):
            for filename in filenames:
                path = os.path.relpath(f"{root}/{filename}")
                if is_ignored(path) or not os.path.isfile(path):
                    continue
                add_file(path)

    with files.get_index() as index:
        for name in filenames:
            if os.path.isfile(name):
                add_file(name)
            elif os.path.isdir(name):
                add_directory(name)


def is_ignored(path):
    return ".gpgit" in path.split("/")
