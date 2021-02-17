from chardet.universaldetector import UniversalDetector
from functools import wraps
from io import BytesIO,BufferedReader,RawIOBase,TextIOWrapper
from re import compile as re_compile
from operator import sub

detector = UniversalDetector()
extractors = {}

def extractor(regex, detect_encoding=False, encoding=None):
    regex = re_compile(regex)
    def decorator(func):
        @wraps(func)
        def wrapper(blob):
            stream = OStreamReader(blob.data_stream)

            if detect_encoding:
                detector.reset()
                cache = BytesIO()

                while data := stream.read(64*1024):
                    cache.write(data)
                    detector.feed(data)
                    if detector.done:
                        break

                cache.seek(0)
                encoding = detector.close().get('encoding')
                stream = ConcatReader(cache, stream)

            if encoding:
                stream = TextIOWrapper(BufferedReader(stream), encoding)

            return func(blob, stream)

        extractors[regex] = wrapper
        return wrapper
    return decorator

def get_best_extractor(mime):
    func = None
    longest = 0

    for regex,f in extractors.items():
        if match := regex.search(mime):
            l = sub(*match.span())
            if l < longest:
                func = f
                longest = l

    return func

class ConcatReader(RawIOBase):
    def __init__(self, *streams):
        self.streams = iter(reversed(streams))
        self.advance()

    def advance(self):
        try:
            self.cur = next(self.streams)
        except StopIteration:
            self.cur = None

    def readable(self):
        return True

    def readinto(self, b):
        while self.cur is not None:
            if l := self.cur.readinto(b):
                return l

            self.advance()

        return 0

class OStreamReader(RawIOBase):
    def __init__(self, stream):
        self.stream = stream

    def readable(self):
        return True

    def readinto(self, b):
        data = self.stream.read(len(b))
        if not data:
            return 0
        l = len(data)
        b[:l] = data
        return l
