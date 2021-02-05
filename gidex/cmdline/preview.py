from uvicorn import run as run_asgi
from ..asgi_app import PreviewApplication

def preview_repository(args):
    run_asgi(
        app=PreviewApplication(
            repo=args.directory,
            debug=args.debug,
        ),
        host='0.0.0.0',
    )
