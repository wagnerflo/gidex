from asyncio import get_running_loop
from dataclasses import dataclass,asdict

async def stream_file(func, *args):
    loop = get_running_loop()
    fp = await loop.run_in_executor(None, func, *args)
    while data := await loop.run_in_executor(None, fp.read, 16384):
        yield data
    await loop.run_in_executor(None, fp.close)

@dataclass(frozen=True)
class ref:
    name: str

    def asdict(self):
        d = asdict(self)
        d.update(type=self.type)
        return d

    @property
    def type(self):
        return self.__class__.__name__

@dataclass(frozen=True)
class workdir(ref):
    def asdict(self):
        return dict(type=self.type)

@dataclass(frozen=True)
class head(ref):
    pass

@dataclass(frozen=True)
class tag(ref):
    pass

@dataclass(frozen=True)
class sha(ref):
    pass
