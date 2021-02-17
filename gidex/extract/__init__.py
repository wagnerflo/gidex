from .util import get_best_extractor
from . import text
from . import pdf

def extract_from_blob(blob):
    if func := get_best_extractor(blob.mime_type):
        print('      using {}.{} for {}'.format(
            func.__module__, func.__qualname__, blob.mime_type))
        return func(blob)

    return None

