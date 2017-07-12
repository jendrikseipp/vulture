import codecs
import os
import tokenize

# Encoding to use when converting input files to unicode.
ENCODING = 'utf-8'


class VultureInputException(Exception):
    pass


def format_path(path):
    if not path:
        return path
    relpath = os.path.relpath(path)
    return relpath if not relpath.startswith('..') else path


def read_file(filename):
    # Python >= 3.2
    try:
        # Use encoding detected by tokenize.detect_encoding().
        with tokenize.open(filename) as f:
            return f.read()
    except (SyntaxError, UnicodeDecodeError) as err:
        raise VultureInputException(err)
    except AttributeError:
        # tokenize.open was added in Python 3.2.
        pass

    # Python < 3.2
    try:
        with codecs.open(filename, encoding=ENCODING) as f:
            return f.read()
    except UnicodeDecodeError as err:
        raise VultureInputException(err)


class LoggingList(list):
    def __init__(self, name, verbose):
        self._name = name
        self._verbose = verbose
        return list.__init__(self)

    def append(self, item):
        if self._verbose:
            print('{0} <- {1}'.format(self._name, item))
        list.append(self, item)
