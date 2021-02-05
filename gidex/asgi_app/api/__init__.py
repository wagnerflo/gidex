from functools import wraps
from starlette.datastructures import Headers
from starlette.exceptions import HTTPException
from starlette.responses import Response,JSONResponse,StreamingResponse
from starlette.routing import Route,Match,Mount

from . import workdir
from ..util import stream_file
from ...util import BreakoutError
from ...consts import (
    API_ACCEPT,
    API_PROFILE,
)

def with_repository(func):
    @wraps(func)
    async def wrapper(self, request):
        repo,name = self.get_repository(request)
        res = await func(self, request, repo)
        if isinstance(res, Response):
            return res
        return JSONResponse({
            'object': res,
            'repository': dict(
                name = name,
            ),
        })
    return wrapper

class ApiRoute(Mount):
    def __init__(self, path, repository_prefix, get_repository):
        self.get_repository = get_repository
        super().__init__(path, routes=[
            Route(
                '/' + repository_prefix + ':/{path:path}',
                self.handle_path_bare,
                methods=('GET', 'HEAD'),
                name='api_contents',
            ),
            Route(
                '/',
                self.handle_path_bare,
                methods=('GET', 'HEAD'),
                name='api_root',
            ),
        ])

    def matches(self, scope):
        if scope['query_string']:
            return super().matches(scope)

        headers = Headers(scope=scope)
        if (headers.get('Accept') == API_ACCEPT and
            headers.get('Accept-Profile') == API_PROFILE):
            return super().matches(scope)

        return Match.NONE, {}

    @with_repository
    async def handle_path_bare(self, request, repo):
        if repo.bare:
            raise HTTPException(404)

        if request.query_params.get('raw') is not None:
            path,_ = workdir.resolve_path(
                repo.working_tree_dir,
                request.path_params['path'],
            )
            return StreamingResponse(
                content=stream_file(path.open, 'rb'),
            )

        try:
            return workdir.path_to_object(
                request,
                repo.working_tree_dir,
                request.path_params['path'],
                recurse=1,
            )
        except BreakoutError:
            raise HTTPException(404)
