import argparse
import sys
import os
import textwrap
from .cli import files
from .cli import base
from .cli import compare
from . import remote
import subprocess


def print_help():
    logo = """
    \033[1;32m
    ░██████╗░██████╗░░░░░░░░██████╗░██╗████████╗
    ██╔════╝░██╔══██╗░░░░░░██╔════╝░██║╚══██╔══╝
    ██║░░██╗░██████╔╝█████╗██║░░██╗░██║░░░██║░░░
    ██║░░╚██╗██╔═══╝░╚════╝██║░░╚██╗██║░░░██║░░░
    ╚██████╔╝██║░░░░░░░░░░░╚██████╔╝██║░░░██║░░░
    ░╚═════╝░╚═╝░░░░░░░░░░░░╚═════╝░╚═╝░░░╚═╝░░░  
    \033[0m
    """ 
    help_text = """
    \033[1;34mgp-git -  A lightweight local version control system for newbies, built in pure Python.\033[0m

    \033[1;33mAvailable commands:\033[0m
      \033[1;36mstart\033[0m         Initializes a new project in your current working directory [\033[1;31minit\033[0m]                   | Usage: \033[1;32mgp-git start\033[0m
      \033[1;36msave\033[0m          Records changes to the repository with a message describing the changes [\033[1;31mcommit\033[0m]     | Usage: \033[1;32mgp-git save "Your commit message"\033[0m
      \033[1;36mthrow\033[0m         Sends your committed changes to the remote repository [\033[1;31mpush\033[0m]                         | Usage: \033[1;32mgp-git throw\033[0m
      \033[1;36mhistory\033[0m       Displays the commit history of the repository [\033[1;31mlog\033[0m]                                  | Usage: \033[1;32mgp-git history\033[0m
      \033[1;36mcombine\033[0m       Merges changes from one branch into another [\033[1;31mmerge\033[0m]                                  | Usage: \033[1;32mgp-git combine branch-name\033[0m
      \033[1;36mfingerprint\033[0m   Computes the object ID (hash) of a file and optionally creates a blob from it [\033[1;31mhash\033[0m] | Usage: \033[1;32mgp-git fingerprint file-name\033[0m
      \033[1;36mview\033[0m          Shows content or type and size information for repository objects [\033[1;31mcat-file\033[0m]         | Usage: \033[1;32mgp-git view object-id\033[0m
      \033[1;36mvis\033[0m           Visualizes commit history using graph structures                                     | Usage: \033[1;32mgp-git vis\033[0m
      \033[1;36mwrite-tree\033[0m    Creates a tree object from the current index                                         | Usage: \033[1;32mgp-git write-tree\033[0m
      \033[1;36mread-tree\033[0m     Reads tree information into the index                                                | Usage: \033[1;32mgp-git read-tree tree-id\033[0m
      \033[1;36mshow\033[0m          Displays various types of objects (commits, trees, blobs, tags)                      | Usage: \033[1;32mgp-git show object-id\033[0m
      \033[1;36mcompare\033[0m       Shows changes between commits, commit and working tree, etc [\033[1;31mdiff\033[0m]                   | Usage: \033[1;32mgp-git compare commit1 commit2\033[0m
      \033[1;36mswitch\033[0m        Switches branches or restores working tree files [\033[1;31mcheckout\033[0m]                          | Usage: \033[1;32mgp-git switch branch-name\033[0m
      \033[1;36mlabel\033[0m         Creates, lists, deletes or verifies a tag object signed with GPG [\033[1;31mtag\033[0m]               | Usage: \033[1;32mgp-git label tag-name\033[0m
    """
    print(logo)
    print(help_text)


def start(args):
    base.start()
    print(f"Created a new gp-git repository in {os.getcwd()}/{files.GPGIT_DIR}")


def fingerprint(args):
    with open(args.file, "rb") as f:
        print(files.fingerprint(f.read()))


def view(args):
    sys.stdout.flush()
    sys.stdout.buffer.write(files.get_object(args.object, expected=None))


def read_tree(args):
    base.read_tree(args.tree)


def write_tree(args):
    print(base.write_tree())


def save(args):
    print(base.save(args.message))


def _print_save(obj_id, save, refs=None):
    refs_str = f' ({", ".join(refs)})' if refs else ""
    print(f"save {obj_id}{refs_str}\n")
    print(textwrap.indent(save.message, "    "))
    print("")


def history(args):
    refs = {}
    for refname, ref in files.iter_refs():
        refs.setdefault(ref.value, []).append(refname)

    for obj_id in base.iter_saves_and_parents({args.obj_id}):
        save = base.get_save(obj_id)
        _print_save(obj_id, save, refs.get(obj_id))


def show(args):
    if not args.obj_id:
        return
    save = base.get_save(args.obj_id)
    parent_tree = None
    if save.parents:
        parent_tree = base.get_save(save.parents[0]).tree
    _print_save(args.obj_id, save)
    result = compare.compare_trees(base.get_tree(parent_tree), base.get_tree(save.tree))
    sys.stdout.flush()
    sys.stdout.buffer.write(result)


def _compare(args):
    obj_id = args.save and base.get_obj_id(args.save)
    if args.save:
        tree_from = base.get_tree(obj_id and base.get_save(obj_id).tree)

    if args.cached:
        tree_to = base.get_index_tree()
        if not args.save:
            obj_id = base.get_obj_id("@")
            tree_from = base.get_tree(obj_id and base.get_save(obj_id).tree)
        else:
            tree_to = base.get_working_tree()
            if not args.save:
                tree_from = base.get_index_tree()

        result = compare.compare_trees(tree_from, tree_to)
        sys.stdout.flush()
        sys.stdout.buffer.write(result)


def switch(args):
    base.switch(args.save)


def label(args):
    base.create_label(args.name, args.obj_id)


def branch(args):
    if not args.name:
        current = base.get_branch_name()
        for branch in base.iter_branch_names():
            prefix = "*" if branch == current else " "
            print(f"{prefix} {branch}")
    else:
        base.create_branch(args.name, args.start_point)
        print(f"Branch {args.name} created at {args.start_point[:10]}")


def vis(args):
    dot = "digraph saves {\n"
    obj_ids = set()

    for refname, ref in files.iter_refs():
        dot += f'"{refname}" [shape=note]\n'
        dot += f'"{refname}" -> "{ref.value}"\n'
        if not ref.symbolic:
            obj_ids.add(ref.value)

    for obj_id in base.iter_saves_and_parents(obj_ids):
        save = base.get_save(obj_id)
        dot += f'"{obj_id}" [shape=box style=filled label="{obj_id[:10]}"]\n'
        for parent in save.parents:
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

    COMBINE_HEAD = files.get_ref("COMBINE_HEAD").value
    if COMBINE_HEAD:
        print(f"Merging with {COMBINE_HEAD[:10]}")

    print("\nChanges to be saved:\n")
    HEAD_tree = HEAD and base.get_save(HEAD).tree
    for path, action in compare.iter_changed_files(
        base.get_tree(HEAD_tree), base.get_index_tree()
    ):
        print(f"{action:>12}: {path}")
    print("\nChanges not staged for save:\n")
    for path, action in compare.iter_changed_files(
        base.get_index_tree(), base.get_working_tree()
    ):
        print(f"{action:>12}: {path}")


def reset(args):
    base.reset(args.save)


def combine(args):
    base.combine(args.save)


def combine_base(args):
    print(base.get_combine_base(args.save1, args.save2))


def download(args):
    remote.download(args.remote)


def throw(args):
    remote.throw(args.remote, f"refs/heads/{args.branch}")


def track(args):
    base.track(args.files)


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command")
    commands.required = True

    obj_id = base.get_obj_id

    start_parser = commands.add_parser("start", help="Creates a new repository")
    start_parser.set_defaults(func=start)

    fingerprint_obj_parser = commands.add_parser("fingerprint")
    fingerprint_obj_parser.set_defaults(func=fingerprint)
    fingerprint_obj_parser.add_argument("file")

    view_parser = commands.add_parser("cat-file")
    view_parser.set_defaults(func=view)
    view_parser.add_argument("object", type=obj_id)

    write_tree_parser = commands.add_parser("write-tree")
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser("read-tree")
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument("tree", type=obj_id)

    save_parser = commands.add_parser("save")
    save_parser.set_defaults(func=save)
    save_parser.add_argument("-m", "--message", required=True)

    history_parser = commands.add_parser("history")
    history_parser.set_defaults(func=history)
    history_parser.add_argument("obj_id", default="@", type=obj_id, nargs="?")

    show_parser = commands.add_parser("show")
    show_parser.set_defaults(func=show)
    show_parser.add_argument("obj_id", default="@", type=obj_id, nargs="?")

    compare_parser = commands.add_parser("compare")
    compare_parser.set_defaults(func=_compare)
    compare_parser.add_argument("--cached", action="store_true")
    compare_parser.add_argument("save", nargs="?")

    switch_parser = commands.add_parser("switch")
    switch_parser.set_defaults(func=switch)
    switch_parser.add_argument("obj_id", type=obj_id)

    label_parser = commands.add_parser("label")
    label_parser.set_defaults(func=label)
    label_parser.add_argument("name")
    label_parser.add_argument("obj_id", default="@", type=obj_id, nargs="?")

    branch_parser = commands.add_parser("branch")
    branch_parser.set_defaults(func=branch)
    branch_parser.add_argument("name")
    branch_parser.add_argument("start_point", default="@", type=obj_id, nargs="?")

    vis_parser = commands.add_parser("vis")
    vis_parser.set_defaults(func=vis)

    status_parser = commands.add_parser("status")
    status_parser.set_defaults(func=status)

    reset_parser = commands.add_parser("reset")
    reset_parser.set_defaults(func=reset)
    reset_parser.add_argument("save", type=obj_id)

    combine_parser = commands.add_parser("combine")
    combine_parser.set_defaults(func=combine)
    combine_parser.add_argument("save", type=obj_id)

    combine_base_parser = commands.add_parser("combine-base")
    combine_base_parser.set_defaults(func=combine_base)
    combine_base_parser.add_argument("save1", type=obj_id)
    combine_base_parser.add_argument("save2", type=obj_id)

    download_parser = commands.add_parser("download")
    download_parser.set_defaults(func=download)
    download_parser.add_argument("remote")

    throw_parser = commands.add_parser("throw")
    throw_parser.set_defaults(func=throw)
    throw_parser.add_argument("remote")
    throw_parser.add_argument("branch")

    track_parser = commands.add_parser("track")
    track_parser.set_defaults(func=track)
    track_parser.add_argument("files", nargs="+")

    help_parser = commands.add_parser("help", help="Show help information")
    help_parser.set_defaults(func=lambda args: print_help())

    with files.change_git_dir('.'):
        args = parser.parse_args()
        args.func(args)

