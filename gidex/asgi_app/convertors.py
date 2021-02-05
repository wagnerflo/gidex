from starlette.convertors import (
    CONVERTOR_TYPES,
    Convertor,
)

class RepositoryConvertor(Convertor):
    regex = '.*(?=/:)'

    def convert(self, value):
        return str(value)

    def to_string(self, value):
        value = str(value)
        assert '/:' not in value, 'May not contain path part starting with colon'
        return value

class EmptyConvertor(Convertor):
    regex = ''

    def convert(self, value):
        return ''

    def to_string(self, value):
        return ''

CONVERTOR_TYPES.update(
    repo = RepositoryConvertor(),
    empty = EmptyConvertor(),
)
