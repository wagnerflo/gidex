from .util import extractor

@extractor(r'^text/', detect_encoding=True)
def text(blob, stream):
    return stream.read()
