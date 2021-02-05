from io import TextIOWrapper
from mimetypes import (
    MimeTypes,
    knownfiles as known_mime_files,
)
from magic import from_buffer as guess_from_bytes
from os.path import isfile
from pkg_resources import resource_stream

PACKAGE_NAME,_,_ = __name__.rpartition('.')
mimedb = MimeTypes(
    filenames=[f for f in known_mime_files if isfile(f)]
)
mimedb.readfp(
    TextIOWrapper(resource_stream(PACKAGE_NAME, 'mime.types'))
)

class BreakoutError(RuntimeError):
    pass

def relative_contained(path, base):
    try:
        return path.relative_to(base)
    except ValueError:
        raise BreakoutError()

def nodot(path):
    path = str(path)
    return '' if path == '.' else path

def dir_sorted(iterator):
    return sorted(iterator, key=lambda i: (not i.is_dir(), i.name))

def guess_mime(filename, fp):
    mime,_ = mimedb.guess_type(filename)
    if mime:
        return mime
    return guess_from_bytes(fp.read(2048), mime=True)
