def preview_repository(args):
    from .asgi_app import PreviewApplication
    from uvicorn import run

    uvicorn.run(
        app=PreviewApplication(
            repo=args.directory,
            debug=args.debug,
        ),
        host='0.0.0.0',
    )

def create_index(args):
    from .index import Index

    if not args.repository_base.is_dir():
        raise Exception('repository base is no directory')

    Index.create(
        path = args.directory,
        repository_base = args.repository_base.resolve(strict=True),
    )

def add_repository(args):
    from .index import Index

    ix = Index.open(args.directory)
    ix.add_repository(
        args.repository,
        incremental=args.incremental,
        print_status=True,
    )

def main():
    from argparse import ArgumentParser
    from pathlib import Path

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(required=True, dest='cmd')

    create_parser = subparsers.add_parser('create')
    create_parser.add_argument(
        '--repository-base',
        type=Path, required=True,
    )
    create_parser.add_argument(
        'directory',
        type=Path,
    )
    create_parser.set_defaults(func=create_index)

    add_parser = subparsers.add_parser('add')
    add_parser.add_argument(
        '-i', '--incremental',
        action='store_true',
    )
    add_parser.add_argument(
        'directory',
        type=Path,
    )
    add_parser.add_argument(
        'repository',
        type=Path,
    )
    add_parser.set_defaults(func=add_repository)

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
