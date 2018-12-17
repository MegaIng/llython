import sys
import traceback
from io import TextIOBase
from pathlib import Path

from lark.exceptions import LarkError

from llython.grammar.level_py.parser import parse, decode_python_source


class MultiStream(TextIOBase):
    def __init__(self, *streams):
        self.streams = streams

    def __getattr__(self, item):
        open("test.txt", "a").write(item)

    def write(self, *args):
        for st in self.streams:
            st.write(*args)

    def flush(self, *args):
        for st in self.streams:
            st.flush(*args)

    @property
    def closed(self):
        return any(st.closed for st in self.streams)


def check_path(folder: Path, ignore=()):
    with Path(__file__).with_name("out.txt").open("w") as out, Path(__file__).with_name("out.txt").open("w") as err:
        out = MultiStream(out, sys.stdout)
        err = MultiStream(err, sys.stderr)
        files = list(folder.rglob("*.py"))
        for i, path in enumerate(files):
            assert path.is_file() and path.suffix == ".py", path
            p = str(path).replace('\\', '/')
            print(f"[{i + 1:4}/{len(files):4}]", p, file=out)
            if any(ig in path.parents for ig in ignore):
                print("Ignore File", p)
            else:
                try:
                    parse(decode_python_source(path.open('rb').read()))
                except LarkError as e:
                    print(f'Error in File "{p}", line {e.line if hasattr(e,"line") else 0}:\n', file=err)
                    traceback.print_exc(file=err)


check_path(Path(r"C:\Program Files\Python37\Lib\site-packages"),
           (Path(r"C:\Program Files\Python37\Lib\lib2to3\tests"),
            Path(r"C:\Program Files\Python37\Lib\site-packages\spacy\lang")))
