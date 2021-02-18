from ...util import as_utc,guess_mime

def tree_sorted(iterator):
    return sorted(iterator, key=lambda i: (i.type == 'blob', i.name))

def resolve_path(repo, ref, rel):
    rtree = repo.tree()

    if ref.type == 'head':
        commit = repo.heads[ref.name].commit

    gobj = commit.tree
    if rel:
        gobj = gobj[rel]

    return gobj,commit

def path_to_object(request, rel, ref, repo, repo_name, with_path=True, recurse=0):
    return gobj_to_object(
        request,
        *resolve_path(repo, ref, rel),
        ref, repo_name,
        with_path=with_path,
        recurse=recurse,
    )

def gobj_to_object(request, gobj, commit, ref, repo_name, with_path=True, recurse=0):
    name = gobj.name
    rel = gobj.path
    obj = dict(
        name = name,
        url = request.url_for('api_stat', repo=repo_name, ref=ref, path=rel),
        raw = request.url_for('api_raw', repo=repo_name, ref=ref, path=rel),
        ignored = False,
        modified = False,
        commit = dict(
            author = commit.author.name,
            email = commit.author.email,
            message = commit.message,
            when = as_utc(commit.committed_datetime).isoformat(),
        ),
        path = [],
    )

    if with_path and rel:
        obj.update(
            path = [
                dict(
                    name = p,
                    url = request.url_for(
                        'api_stat', repo=repo_name, ref=ref, path=p
                    ),
                )
                for p in [''] + rel.split('/')[:-1]
            ],
        )

    if gobj.type == 'tree':
        obj.update(
            object_type = 'tree',
        )

        if recurse:
            rec = max(0, recurse - 1)
            obj.update(
                children = [
                    gobj_to_object(
                        request, child, commit, ref, repo_name,
                        with_path=False,
                        recurse=rec,
                    )
                    for child in tree_sorted(gobj)
                ],
            )

    elif gobj.type == 'blob':
        obj.update(
            object_type = 'blob',
            mime_type = guess_mime(name),
        )

    return obj
