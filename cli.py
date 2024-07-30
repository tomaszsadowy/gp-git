import argparse
import sys
import os
import textwrap
import files
import base
import diff
import remote
import subprocess


def init(args):
    base.init()
    print(f"Initialized a new zgit repository in {os.getcwd()}/{files.ZGIT_DIR}")


def hash_object(args):
    with open(args.file, "rb") as f:
        print(files.hash_object(f.read()))


def cat_file(args):
    sys.stdout.flush()
    sys.stdout.buffer.write(files.get_object(args.object, expected=None))


def write_tree(args):
    print(base.write_tree())


def read_tree(args):
    base.read_tree(args.tree)


def commit(args):
    print(base.commit(args.message))


def _print_commit(obj_id, commit, refs=None):
    refs_str = f' ({", ".join(refs)})' if refs else ""
    print(f"commit {obj_id}{refs_str}\n")
    print(textwrap.indent(commit.message, "    "))
    print("")


def log(args):
    refs = {}
    for refname, ref in files.iter_refs():
        refs.setdefault(ref.value, []).append(refname)

    for obj_id in base.iter_commits_and_parents({args.obj_id}):
        commit = base.get_commit(obj_id)
        _print_commit(obj_id, commit, refs.get(obj_id))


def show(args):
    if not args.obj_id:
        return
    commit = base.get_commit(args.obj_id)
    parent_tree = None
    if commit.parents:
        parent_tree = base.get_commit(commit.parents[0]).tree
    _print_commit(args.obj_id, commit)
    result = diff.diff_trees(base.get_tree(parent_tree), base.get_tree(commit.tree))
    sys.stdout.flush()
    sys.stdout.buffer.write(result)


def _diff(args):
    obj_id = args.commit and base.get_obj_id(args.commit)
    if args.commit:
        tree_from = base.get_tree(obj_id and base.get_commit(obj_id).tree)

    if args.cached:
        tree_to = base.get_index_tree()
        if not args.commit:
            obj_id = base.get_obj_id("@")
            tree_from = base.get_tree(obj_id and base.get_commit(obj_id).tree)
        else:
            tree_to = base.get_working_tree()
            if not args.commit:
                tree_from = base.get_index_tree()

        result = diff.diff_trees(tree_from, tree_to)
        sys.stdout.flush()
        sys.stdout.buffer.write(result)


def checkout(args):
    base.checkout(args.commit)


def tag(args):
    base.create_tag(args.name, args.obj_id)


def branch(args):
    if not args.name:
        current = base.get_branch_name()
        for branch in base.iter_branch_names():
            prefix = "*" if branch == current else " "
            print(f"{prefix} {branch}")
    else:
        base.create_branch(args.name, args.start_point)
        print(f"Branch {args.name} created at {args.start_point[:10]}")


def k(args):
    dot = "digraph commits {\n"
    obj_ids = set()

    for refname, ref in files.iter_refs():
        dot += f'"{refname}" [shape=note]\n'
        dot += f'"{refname}" -> "{ref.value}"\n'
        if not ref.symbolic:
            obj_ids.add(ref.value)

    for obj_id in base.iter_commits_and_parents(obj_ids):
        commit = base.get_commit(obj_id)
        dot += f'"{obj_id}" [shape=box style=filled label="{obj_id[:10]}"]\n'
        for parent in commit.parents:
            dot += f'"{obj_id}" -> "{parent}"\n'

    dot += "}"
    print(dot)

    with subprocess.Popen(
        ["dot", "-fgtk", "/dev/stdin"], stdin=subprocess.PIPE
    ) as proc:
        proc.communicate(dot.encode())


def status(args):
    HEAD = base.get_obj_id("@")
    branch = base.get_branch_name()
    if branch:
        print(f"On branch {branch}")
    else:
        print(f"HEAD detached at {HEAD[:10]}")

    MERGE_HEAD = files.get_ref("MERGE_HEAD").value
    if MERGE_HEAD:
        print(f"Merging with {MERGE_HEAD[:10]}")

    print("\nChanges to be commited:\n")
    HEAD_tree = HEAD and base.get_commit(HEAD).tree
    for path, action in diff.iter_changed_files(
        base.get_tree(HEAD_tree), base.get_index_tree()
    ):
        print(f"{action:>12}: {path}")
    print("\nChanges not stages for commit:\n")
    for path, action in diff.iter_changed_files(
        base.get_index_tree(), base.get_working_tree()
    ):
        print(f"{action:>12}: {path}")


def reset(args):
    base.reset(args.commit)


def merge(args):
    base.merge(args.commit)


def merge_base(args):
    print(base.get_merge_base(args.commit1, args.commit2))


def fetch(args):
    remote.fetch(args.remote)


def push(args):
    remote.push(args.remote, f"refs/heads/{args.branch}")


def add(args):
    base.add(args.files)


def main():
    parser = argparse.ArgumentParser(prog="zgit")
    commands = parser.add_subparsers(dest="command")
    commands.required = True

    obj_id = base.get_obj_id

    init_parser = commands.add_parser("init", help="Initialize a new repository")
    init_parser.set_defaults(func=init)

    hash_obj_parser = commands.add_parser("hash-object")
    hash_obj_parser.set_defaults(func=hash_object)
    hash_obj_parser.add_argument("file")

    cat_file_parser = commands.add_parser("cat-file")
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument("object", type=obj_id)

    write_tree_parser = commands.add_parser("write-tree")
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser("read-tree")
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument("tree", type=obj_id)

    commit_parser = commands.add_parser("commit")
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument("-m", "--message", required=True)

    log_parser = commands.add_parser("log")
    log_parser.set_defaults(func=log)
    log_parser.add_argument("obj_id", default="0", type=obj_id, nargs="?")

    show_parser = commands.add_parser("show")
    show_parser.set_defaults(func=show)
    show_parser.add_argument("obj_id", default="0", type=obj_id, nargs="?")

    diff_parser = commands.add_parser("diff")
    diff_parser.set_defaults(func=_diff)
    diff_parser.add_argument("--cached", action="store_true")
    diff_parser.add_argument("commit", nargs="?")

    checkout_parser = commands.add_parser("checkout")
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument("obj_id", type=obj_id)

    tag_parser = commands.add_parser("tag")
    tag_parser.set_defaults(func=tag)
    tag_parser.add_argument("name")
    tag_parser.add_argument("obj_id", default="0", type=obj_id, nargs="?")

    branch_parser = commands.add_parser("branch")
    branch_parser.set_defaults(func=branch)
    branch_parser.add_argument("name")
    branch_parser.add_argument("start_point", default="0", type="obj_id", nargs="?")

    k_parser = commands.add_parser("k")
    k_parser.set_defaults(func=k)

    status_parser = commands.add_parser("status")
    status_parser.set_defaults(func=status)

    reset_parser = commands.add_parser("reset")
    reset_parser.set_defaults(func=reset)
    reset_parser.add_argument("commit", type=obj_id)

    merge_parser = commands.add_parser("merge")
    merge_parser.set_defaults(func=merge)
    merge_parser.add_argument("commit", type=obj_id)

    merge_base_parser = commands.add_parser("merge-base")
    merge_base_parser.set_defaults(func=merge_base)
    merge_base_parser.add_argument("commit1", type=obj_id)
    merge_base_parser.add_argument("commit2", type=obj_id)

    fetch_parser = commands.add_parser("fetch")
    fetch_parser.set_defaults(func=fetch)
    fetch_parser.add_argument("remote")

    push_parser = commands.add_parser("push")
    push_parser.set_defaults(func=push)
    push_parser.add_argument("remote")
    push_parser.add_argument("branch")

    add_parser = commands.add_parser("add")
    add_parser.set_defaults(func=add)
    add_parser.add_argument("files", nargs="+")

    args = parser.parse_args()
    args.func(args)
