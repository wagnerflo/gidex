from base64 import b64encode
from pathlib import Path

from ...util import (
    relative_contained,
    nodot,
    dir_sorted,
    guess_mime,
)

def resolve_path(base, rel):
    path = Path(base, rel).resolve()
    return path,relative_contained(path, base)

def path_to_object(request, base, rel, with_path=True, recurse=0):
    path,rel = resolve_path(base, rel)
    nrel = nodot(rel)
    obj = dict(
        name = rel.name,
        url = request.url_for('api_stat', repo='', ref=None, path=nrel),
        raw = request.url_for('api_raw', repo='', ref=None, path=nrel),
    )

    if with_path:
        obj.update(
            path = [
                dict(
                    name = p.name,
                    url = request.url_for(
                        'api_stat', repo='', ref=None, path=p.name
                    ),
                )
                for p in reversed(rel.parents)
            ],
        )

    if path.is_file():
        with path.open('rb') as fp:
            obj.update(
                object_type = 'blob',
                mime_type = guess_mime(rel.name, fp)
            )

    elif path.is_dir():
        obj.update(
            object_type = 'tree',
        )

        if recurse:
            rec = max(0, recurse - 1)
            obj.update(
                children = [
                    path_to_object(
                        request, base, child,
                        with_path=False,
                        recurse=rec,
                    )
                    for child in dir_sorted(path.iterdir())
                ],
            )

    else:
        obj.update(
            object_type = 'none',
        )

    return obj
