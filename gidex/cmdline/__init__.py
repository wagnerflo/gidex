from argparse import ArgumentParser
from pathlib import Path

from .preview import preview_repository

def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(required=True, dest='cmd')

    # create_parser = subparsers.add_parser('create')
    # create_parser.add_argument(
    #     '--repository-base',
    #     type=Path, required=True,
    # )
    # create_parser.add_argument(
    #     'directory',
    #     type=Path,
    # )
    # create_parser.set_defaults(func=create_index)

    # add_parser = subparsers.add_parser('add')
    # add_parser.add_argument(
    #     '-i', '--incremental',
    #     action='store_true',
    # )
    # add_parser.add_argument(
    #     'directory',
    #     type=Path,
    # )
    # add_parser.add_argument(
    #     'repository',
    #     type=Path,
    # )
    # add_parser.set_defaults(func=add_repository)

    preview_parser = subparsers.add_parser('preview')
    preview_parser.add_argument(
        '-d', '--debug',
        action='store_true',
    )
    preview_parser.add_argument(
        'directory',
        type=Path,
        default=Path(),
        nargs='?'
    )
    preview_parser.set_defaults(func=preview_repository)

    args = parser.parse_args()
    return args.func(args)
