import argparse
import os
import files

def init(args):
    files.init()
    print(f'Initialized a new zgit repository in {os.getcwd()}/{files.ZGIT_DIR}')

def commit(args):
    print('commit')

def hash_object(args):
    with open(args.file, 'rb') as f:
        print(files.hash_object(f.read()))

def main():
    parser = argparse.ArgumentParser(prog='zgit')
    commands = parser.add_subparsers(dest='command')
    commands.required = True

    init_parser = commands.add_parser('init', help='Initialize a new repository')
    init_parser.set_defaults(func=init)

    commit_parser = commands.add_parser('commit', help='Commit changes')
    commit_parser.add_argument('-m', '--message', required=True, help='Commit message')
    commit_parser.set_defaults(func=commit)

    hash_obj_parser = commands.add_parser('hash-object')
    hash_obj_parser.add_argument('file')
    hash_obj_parser.set_defaults(func=hash_object)

    args = parser.parse_args()
    args.func(args)

