from base64 import b64encode
from pathlib import Path

from ..util import workdir
from ...util import (
    relative_contained,
    nodot,
    dir_sorted,
    guess_mime,
    as_utc
)

def resolve_path(base, rel):
    path = Path(base, rel).resolve()
    return path,relative_contained(path, base)

def path_to_object(request, base, rel, repo, with_path=True, recurse=0):
    path,rel = resolve_path(base, rel)
    wd = workdir(None)
    rtree = repo.tree()
    srel = str(rel)
    nrel = nodot(rel)
    obj = dict(
        name = rel.name,
        url = request.url_for('api_stat', repo='', ref=wd, path=nrel),
        raw = request.url_for('api_raw', repo='', ref=wd, path=nrel),
        ignored = (
            bool(repo.ignored(rel)) or
            nrel == '.git'
        ),
        modified = (
            bool(repo.index.diff("HEAD", paths=[srel])) or
            bool(repo.index.diff(None, paths=[srel]))
        )
    )

    try:
        commit = next(repo.iter_commits(paths=[srel], max_count=1))
    except StopIteration:
        commit = None

    if commit:
        obj.update(
            commit = dict(
                author = commit.author.name,
                email = commit.author.email,
                message = commit.message,
                when = as_utc(commit.committed_datetime).isoformat(),
            ),
        )

    if with_path:
        obj.update(
            path = [
                dict(
                    name = p.name,
                    url = request.url_for(
                        'api_stat', repo='', ref=wd, path=p.name
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
                        request, base, child, repo,
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
