from re import compile
from starlette.convertors import (
    CONVERTOR_TYPES,
    Convertor,
)

from .util import ref,head,tag,sha,workdir

class RefConvertor(Convertor):
    regex = '(?:(head|tag)\/([^:]+)|(sha)\/([0-9a-fA-F]{5,40})|(workdir))?:'
    re = compile(regex)

    def convert(self, value):
        t1,n1,t2,n2,t3 = self.re.fullmatch(value).groups()
        type = t1 or t2 or t3
        name = n1 or n2
        if type is None:
            type = 'workdir'
        return globals()[type](name)

    def to_string(self, value):
        assert isinstance(value, ref), 'Must be ref or subclass'
        if isinstance(value, workdir):
            return 'workdir:'
        return f'{value.type}/{value.name}:'

class EmptyConvertor(Convertor):
    regex = ''

    def convert(self, value):
        return ''

    def to_string(self, value):
        return ''

CONVERTOR_TYPES.update(
    ref = RefConvertor(),
    empty = EmptyConvertor(),
)
