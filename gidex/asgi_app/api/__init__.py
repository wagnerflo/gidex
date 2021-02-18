from functools import wraps
from starlette.datastructures import Headers,QueryParams,URLPath
from starlette.exceptions import HTTPException
from starlette.responses import Response,JSONResponse,StreamingResponse
from starlette.routing import Route,Match

from . import (
    workdir as from_workdir,
    repository as from_repository,
)
from ..util import (
    stream_file,
    head,
    tag,
    workdir,
)
from ...util import (
    guess_mime,
    BreakoutError,
    OStreamReader,
)
from ...consts import (
    API_ACCEPT,
    API_PROFILE,
)

API_HEADERS = {
    'Accept': API_ACCEPT,
    'Accept-Profile': API_PROFILE,
}

class RepositoryResponse(JSONResponse):
    def __init__(self, request, object):
        repo = request.scope.get('repo')
        repo_name = request.scope.get('repo_name')
        ref = request.scope.get('ref')
        route = request.scope.get('route')
        super().__init__(
            dict(
                object = object,
                repository = dict(
                    name = repo_name,
                    is_bare = repo.bare,
                    workdir = route.reverse(request, ref=workdir(None)),
                    heads = [
                        dict(
                            name = h.name,
                            url = route.reverse(request, ref=head(h.name)),
                        )
                        for h in repo.heads
                    ],
                    tags = [

                    ],
                    ref = ref.asdict(),
                ),
            )
        )

class ApiRoute(Route):
    def __init__(self, *args, **kws):
        self._headers = kws.pop('headers', None)
        self._query_param = kws.pop('query_param', None)
        super().__init__(*args, **kws)

    def matches(self, scope):
        if self._headers:
            headers = Headers(scope=scope)
            for k,v in self._headers.items():
                if headers.get(k) != v:
                    return Match.NONE, {}

        if self._query_param:
            if self._query_param not in QueryParams(scope['query_string']):
                return Match.NONE, {}

        return super().matches(scope)

    async def handle(self, scope, receive, send):
        scope.update(
            route = self,
        )
        await super().handle(scope, receive, send)

    def url_path_for(self, name, **path_params):
        url_path = super().url_path_for(name, **path_params)
        if self._query_param:
            return URLPath(f'{url_path}?{self._query_param}')
        return url_path

    def reverse(self, request, **replace):
        path_params = dict(request.path_params)
        path_params.update(**replace)
        url_path = self.url_path_for(self.name, **path_params)
        return url_path.make_absolute_url(base_url=request.base_url)

def ApiRoutes(prefix, repository_prefix, get_repository):
    if prefix[-1] != '/':
        prefix = prefix + '/'

    def with_repository(func):
        @wraps(func)
        async def wrapper(request):
            repo,repo_name = get_repository(request)
            ref = request.path_params.get('ref')
            request.scope.update(
                repo = repo,
                repo_name = repo_name,
                ref = ref,
            )
            return await func(request, repo, repo_name, ref)
        return wrapper

    yield ApiRoute(
        prefix + repository_prefix + '{ref:ref}/{path:path}',
        with_repository(raw),
        methods=('GET', 'HEAD'),
        query_param='raw',
        name='api_raw',
    )
    yield ApiRoute(
        prefix + repository_prefix + '{ref:ref}/{path:path}',
        with_repository(stat),
        methods=('GET', 'HEAD'),
        headers=API_HEADERS,
        name='api_stat',
    )
    yield ApiRoute(
        prefix,
        with_repository(stat),
        methods=('GET', 'HEAD'),
        headers=API_HEADERS,
        name='api_root',
    )

async def raw(request, repo, repo_name, ref):
    if not ref.name:
        if repo.bare:
            raise HTTPException(404)

        path,_ = from_workdir.resolve_path(
            repo.working_tree_dir,
            request.path_params['path'],
        )
        return StreamingResponse(
            content=stream_file(path.open, 'rb'),
            media_type=guess_mime(path.name),
        )

    blob,_ = from_repository.resolve_path(
        repo, ref, request.path_params['path']
    )
    return StreamingResponse(
        content=stream_file(OStreamReader, blob.data_stream),
        media_type=guess_mime(blob.name),
    )

async def stat(request, repo, repo_name, ref):
    if not ref.name:
        if repo.bare:
            raise HTTPException(404)

        try:
            return RepositoryResponse(
                request,
                from_workdir.path_to_object(
                    request,
                    repo.working_tree_dir,
                    request.path_params['path'],
                    repo,
                    recurse=1,
                ),
            )
        except BreakoutError:
            raise HTTPException(404)

    return RepositoryResponse(
        request,
        from_repository.path_to_object(
            request,
            request.path_params['path'],
            ref,
            repo,
            repo_name,
            recurse=1,
        ),
    )
