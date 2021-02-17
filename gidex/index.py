from enum import Enum
from dataclasses import (
    dataclass,
    fields as dataclass_fields
)
from functools import partial
from json import (
    dump as json_write,
    load as json_load,
)
from pathlib import Path
from whoosh.analysis import StandardAnalyzer
from whoosh.index import FileIndex
from whoosh.fields import *
from whoosh.filedb.filestore import FileStorage
from whoosh.query import Term
from whoosh.searching import Searcher

from .util import (
    relative_contained,
    as_utc,
)

class SchemaType(Enum):
    REPOSITORY = 1
    COMMIT = 2
    BLOB = 3

class ForwardingAnalyzer:
    def __init__(self, *, default_analyzer=StandardAnalyzer()):
        self.default_analyzer = default_analyzer

    def __call__(self, value, **kwargs):
        if value is None:
            return None

        if isinstance(value, tuple):
            analyzer,value = value
        else:
            analyzer = self.default_analyzer

        return analyzer(value, **kwargs)

class RepositorySchema(SchemaClass):
    type = NUMERIC(stored=True, signed=False)

    # contents depend on type
    #   REPOSITORY: name == path relative to repository_base
    #   COMMIT: commit sha
    #   BLOB: file path
    identifier = ID(stored=True)

    # repository document
    repository = ID(stored=True)

    # commit only
    author_name = TEXT(stored=True)
    author_email = ID(stored=True)
    author_datetime = DATETIME(stored=True)
    committer_name = TEXT(stored=True)
    committer_email = ID(stored=True)

    authored_datetime = DATETIME(stored=True)
    committed_datetime = DATETIME(stored=True)

    commit_message = TEXT(stored=True)

    # blob only
    blob_content = TEXT(analyzer=ForwardingAnalyzer())

@dataclass(frozen=True, init=False)
class Config:
    gidex_schema: int
    repository_base: Path

    def __init__(self, dct):
        for f in dataclass_fields(self):
            object.__setattr__(self, f.name, f.type(dct[f.name]))

class Index(FileIndex):
    @classmethod
    def gidex_config_file(cls, path):
        return path / 'gidex.conf'

    @classmethod
    def create(cls, *, path, repository_base):
        path = path.resolve()
        if path.exists():
            raise Exception('path already exists')

        path.mkdir()
        conf = {
            'gidex_schema': 1,
            'repository_base': str(repository_base),
        }

        with cls.gidex_config_file(path).open('w') as fp:
            json_write(conf, fp)

        store = FileStorage(str(path))
        store.create_index(RepositorySchema)

    @classmethod
    def open(cls, path):
        with cls.gidex_config_file(path).open('r') as fp:
            conf = Config(json_load(fp))

        store = FileStorage(str(path))
        return store.open_index(indexclass=partial(cls, conf))

    def __init__(self, conf, *args, **kwargs):
        self.gidex_conf = conf
        super().__init__(*args, **kwargs)


    def add_repository(self, path, incremental=False, print_status=False):
        try:
            repo_base = self.gidex_conf.repository_base
            path = relative_contained(path, repo_base)

        except BreakoutError:
            raise Exception('repository is not under {}'.format(repo_base))

        repo_id = str(path)
        repo = Repo(repo_id)

        if not incremental:
            with ix.searcher() as searcher:
                writer = ix.writer()

                for doc in searcher.document_numbers(repository=repo_id):
                    writer.delete_document(doc)

                writer.commit()

        with ix.searcher() as searcher:
            writer = ix.writer()

            repo_doc = searcher.document_number(
                type = SchemaType.REPOSITORY.value,
                identifier = repo_id,
            )

            if repo_doc is None:
                writer.add_document(
                    type = SchemaType.REPOSITORY.value,
                    identifier = repo_id,
                )

            if print_status:
                print('indexing repository {}'.format(repo_id))

            for commit in repo.iter_commits('--all'):
                doc = searcher.document_number(
                    type = SchemaType.COMMIT.value,
                    repository = repo_id,
                    identifier = commit.hexsha,
                )

                if doc is not None:
                    continue

                if print_status:
                    print('  indexing commit {}'.format(commit.hexsha))

                writer.add_document(
                    type = SchemaType.COMMIT.value,
                    repository = repo_id,
                    identifier = commit.hexsha,
                    author_name = commit.author.name,
                    author_email = commit.author.email,
                    committer_name = commit.committer.name,
                    committer_email = commit.committer.email,
                    authored_datetime = as_utc(commit.authored_datetime),
                    committed_datetime = as_utc(commit.committed_datetime),
                    commit_message = commit.message,
                )

                for filename in commit.stats.files.keys():
                    blob = commit.tree[filename]

                    doc = searcher.document_number(
                        type = SchemaType.BLOB.value,
                        repository = repo_id,
                        identifier = blob.hexsha,
                    )

                    if doc is not None:
                        continue

                    if print_status:
                        print('    indexing blob {}'.format(blob.hexsha))

                    writer.add_document(
                        type = SchemaType.BLOB.value,
                        repository = repo_id,
                        identifier = blob.path,
                        blob_content = extract_from_blob(blob),
                    )

            writer.commit()
