try:
    from ..common.path import PATH
except ImportError:
    from src.common.path import PATH
import csscompressor, jsmin, os


def minifyCss():
    for _dir, _folder, _files in os.walk(PATH.DOCS):
        for _file in _files:
            if _file.endswith('css') and not _file.endswith('.min.css'):
                with open(os.path.join(_dir, _file), 'r', encoding='utf-8') as file:
                    src = file.read()
                with open(os.path.join(_dir, _file.replace(".css", ".min.css")), "w") as file:
                    file.write(csscompressor.compress(src))

# TODO
def minifyJs():
    return


if __name__ == "__main__":
    minifyCss()
