from collections.abc import Iterable
from dataclasses import dataclass,asdict
from re import compile
from starlette.convertors import (
    CONVERTOR_TYPES,
    Convertor,
)

@dataclass(frozen=True)
class ref:
    type: str
    name: str

    def asdict(self):
        return asdict(self)

class RepositoryConvertor(Convertor):
    regex = '.*(?=/:)'

    def convert(self, value):
        return str(value)

    def to_string(self, value):
        value = str(value)
        assert '/:' not in value, 'May not contain path part starting with colon'
        return value

class RefConvertor(Convertor):
    value_regex = ':(?:(?:([tsb]):)?([^:]+)|):'
    re = compile(value_regex)
    regex = value_regex + '(?=/)'

    def convert(self, value):
        return ref(*self.re.fullmatch(value).groups())

    def to_string(self, value):
        assert not isinstance(value, str), 'May not be a string'
        if value is None:
            return '::'
        if isinstance(value, dict):
            value = ref(**value)
        elif isinstance(value, Iterable):
            value = ref(*value)
        return f':{value.type}:{value.name}:'

class EmptyConvertor(Convertor):
    regex = ''

    def convert(self, value):
        return ''

    def to_string(self, value):
        return ''

CONVERTOR_TYPES.update(
    repo = RepositoryConvertor(),
    ref = RefConvertor(),
    empty = EmptyConvertor(),
)
