import argparse
import sys
import os

import files
import base


# git init
def init(args):
    files.init()
    print(f"Initialized a new zgit repository in {os.getcwd()}/{files.ZGIT_DIR}")


def hash_object(args):
    with open(args.file, "rb") as f:
        print(files.hash_object(f.read()))


def commit(args):
    print("commit")


def cat_file(args):
    sys.stdout.flush()
    sys.stdout.buffer.write(files.get_object(args.object, expected=None))


def write_tree(args):
   print(base.write_tree())


def read_tree(args):
    base.read_tree(args.tree)

def main():
    parser = argparse.ArgumentParser(prog="zgit")
    commands = parser.add_subparsers(dest="command")
    commands.required = True

    init_parser = commands.add_parser("init", help="Initialize a new repository")
    init_parser.set_defaults(func=init)

    commit_parser = commands.add_parser("commit", help="Commit changes")
    commit_parser.add_argument("-m", "--message", required=True, help="Commit message")
    commit_parser.set_defaults(func=commit)

    hash_obj_parser = commands.add_parser("hash-object")
    hash_obj_parser.set_defaults(func=hash_object)
    hash_obj_parser.add_argument("file")

    cat_file_parser = commands.add_parser("cat-file")
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument("object")

    write_tree_parser = commands.add_parser('write-tree')
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser('read-tree')
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument('tree')


    args = parser.parse_args()
    args.func(args)
