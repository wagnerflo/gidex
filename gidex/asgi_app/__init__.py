from abc import abstractmethod
from asyncio import get_running_loop
from dataclasses import MISSING
from git import Repo
from pathlib import Path
from pkg_resources import resource_exists,resource_stream
from starlette.applications import Starlette
from starlette.config import Config
from starlette.responses import StreamingResponse,Response
from starlette.routing import Route

from . import convertors
from .util import stream_file
from .api import ApiRoute
from ..consts import (
    SCRIPT_NAME,
    SCRIPT_NAME_MIN,
)

PACKAGE_NAME,_,_ = __name__.rpartition('.')

ASSET_ENTRY = 'ui.html'
ASSET_MIMETYPES = (
    ('.css', 'text/css'),
    ('.js.map', 'application/json'),
    ('.js', 'application/javascript'),
)

config = Config()

def guess_mimetype(name):
    for end,mime in ASSET_MIMETYPES:
        if name.endswith(end):
            return mime

class BaseApplication(Starlette):
    def __init__(self, api_only=MISSING, api_uri=MISSING, debug=MISSING):
        self._api_only = api_only
        self._api_uri = api_uri
        self._set_debug = debug
        super().__init__(
            on_startup=[
                self.load_env,
                self.on_startup,
                self.setup_routes,
            ],
        )

    async def load_env(self):
        if self._api_only is MISSING:
            self._api_only = config('GIDEX_API_ONLY', cast=bool, default=False)

        if self._api_uri is MISSING:
            self._api_uri = config('GIDEX_API_URI', default=None)

        if self._set_debug is MISSING:
            self._set_debug = config('DEBUG', cast=bool, default=False)

        self.debug = self._set_debug
        self.script_name = SCRIPT_NAME if self.debug else SCRIPT_NAME_MIN

    async def on_startup(self):
        pass

    async def setup_routes(self):
        if not self._api_only:
            self.routes.append(
                Route(
                    '/$/{filename:path}', self.handle_asset,
                    methods=('GET', 'HEAD'),
                    name='static',
                )
            )

        self.routes.append(
            ApiRoute(
                '/',
                self.repository_route_prefix,
                self.get_repository,
            )
        )

        if not self._api_only:
            self.routes.append(
                Route('/{path:path}', self.handle_asset, methods=('GET', 'HEAD'))
            )

    async def handle_asset(self, request):
        loop = get_running_loop()
        name = 'assets/' + request.path_params.get('filename', ASSET_ENTRY)

        if not await loop.run_in_executor(
                         None, resource_exists, PACKAGE_NAME, name):
            return Response(status_code=404)

        mime = guess_mimetype(name)
        root_url = request.url_for('api_root')
        headers = {
            'gidex-script-name': self.script_name,
            'gidex-ui-root': root_url,
            'gidex-api-root': root_url if self._api_uri is None else self._api_uri,
            'gidex-static-root': request.url_for('static', filename='')
        }

        if request.method == 'HEAD':
            return Response(media_type=mime, headers=headers)

        return StreamingResponse(
            content=stream_file(resource_stream, PACKAGE_NAME, name),
            media_type=mime,
            headers=headers,
        )

    @abstractmethod
    def get_repository(self, request):
        pass

class Application(BaseApplication):
    repository_route_prefix = '{repo:repo}/'

    def __init__(self, index=MISSING, api_only=MISSING, api_uri=MISSING, debug=MISSING):
        self._index = index
        super().__init__(api_only, api_uri, debug)

    async def on_startup(self):
        if self._index is MISSING:
            self._index = config('GIDEX_INDEX_PATH', cast=Path)

        print('init index')

class PreviewApplication(BaseApplication):
    repository_route_prefix = '{repo:empty}'

    def __init__(self, repo=MISSING, debug=MISSING):
        self._repo = repo
        super().__init__(debug=debug)

    async def on_startup(self):
        if self._repo is MISSING:
            self._repo = config(
                'GIDEX_PREVIEW_PATH', cast=Path, default=Path('.')
            )

        self._repo = self._repo.resolve()
        self._repo_name = self._repo.name
        self._repo = Repo(self._repo)

    def get_repository(self, request):
        return self._repo,self._repo_name
