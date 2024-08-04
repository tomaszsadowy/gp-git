import subprocess
from collections import defaultdict
from tempfile import NamedTemporaryFile as Temp
from . import files


def compare_trees(*trees):
    entries = defaultdict(lambda: [None] * len(trees))
    for i, tree in enumerate(trees):
        for path, oid in tree.items():
            entries[path][i] = oid

    for path, obj_ids in entries.items():
        yield (path, *obj_ids)


def iter_changed_files(t_from, t_to):
    for path, o_from, o_to in compare_trees(t_from, t_to):
        if o_from != o_to:
            action = "new file" if not o_from else "deleted" if not o_to else "modified"
            yield path, action


def compare_trees(t_from, t_to):
    output = b""
    for path, o_from, o_to in compare_trees(t_from, t_to):
        if o_from != o_to:
            output += compare_blobs(o_from, o_to, path)
    return output


def compare_blobs(o_from, o_to, path="blob"):
    with Temp() as f_from, Temp() as f_to:
        for obj_id, f in ((o_from, f_from), (o_to, f_to)):
            if obj_id:
                f.write(files.get_object(obj_id))
                f.flush()

        with subprocess.Popen(
            [
                "compare",
                "--unified",
                "--show-c-function",
                "--label",
                f"a/{path}",
                f_from.name,
                "--label",
                f"b/{path}",
                f_to.name,
            ],
            stdout=subprocess.PIPE,
        ) as proc:
            output, _ = proc.communicate()

        return output


def combine_trees(t_base, t_HEAD, t_other):
    tree = {}
    for path, o_base, o_HEAD, o_other in compare_trees(t_base, t_HEAD, t_other):
        tree[path] = files.fingerprint(combine_blobs(o_base, o_HEAD, o_other))
    return tree


def combine_blobs(o_base, o_HEAD, o_other):
    with Temp() as f_base, Temp() as f_HEAD, Temp() as f_other:

        for oid, f in ((o_base, f_base), (o_HEAD, f_HEAD), (o_other, f_other)):
            if oid:
                f.write(files.get_object(oid))
                f.flush()

        with subprocess.Popen(
            [
                "compare3",
                "-m",
                "-L",
                "HEAD",
                f_HEAD.name,
                "-L",
                "BASE",
                f_base.name,
                "-L",
                "COMBINE_HEAD",
                f_other.name,
            ],
            stdout=subprocess.PIPE,
        ) as proc:
            output, _ = proc.communicate()
            assert proc.returncode in (0, 1)

        return output
