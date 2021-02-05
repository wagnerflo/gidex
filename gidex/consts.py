from json import load
from pathlib import Path

with Path(__file__).with_suffix('.json').open() as fp:
    for key,value in load(fp).items():
        globals()[key] = value
