import argparse
import os
import files

def init(args):
    files.init()
    print(f'Initialized a new zgit repository in {os.getcwd()}/{files.ZGIT_DIR}')

def commit(args):
    print('commit')

def main():
    parser = argparse.ArgumentParser(prog='zgit')
    commands = parser.add_subparsers(dest='command')
    commands.required = True

    init_parser = commands.add_parser('init', help='Initialize a new repository')
    init_parser.set_defaults(func=init)

    commit_parser = commands.add_parser('commit', help='Commit changes')
    commit_parser.add_argument('-m', '--message', required=True, help='Commit message')
    commit_parser.set_defaults(func=commit)

    args = parser.parse_args()
    args.func(args)

