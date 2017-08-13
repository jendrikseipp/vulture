import ast
import codecs
import os
import tokenize

# Encoding to use when converting input files to unicode.
ENCODING = 'utf-8'


class VultureInputException(Exception):
    pass


def condition_is_always_true(condition):
    try:
        return _evaluate_condition(condition)
    except ValueError:
        return False


def condition_is_always_false(condition):
    try:
        return not _evaluate_condition(condition)
    except ValueError:
        return False


def _evaluate_condition(condition):
    """
    Try to safely evaluate the given condition. Return True or False if
    the if the given condition is always True or False, respectively.
    Raise ``ValueError`` if the condition cannot be evaluated safely.

    The evaluation will only succeed if the condition exclusively
    consists of Python literals. We could use eval() to catch more
    cases. However, this function is not safe for arbitrary Python code.
    Even after overwriting the "__builtins__" dictionary, the original
    dictionary can be restored
    (https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html).

    """
    try:
        result = bool(ast.literal_eval(condition))
    except ValueError:
        raise ValueError("Condition cannot be evaluated")
    else:
        return result


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
    def __init__(self, typ, verbose):
        self.typ = typ
        self._verbose = verbose
        return list.__init__(self)

    def append(self, item):
        if self._verbose:
            print('define {0} "{1}"'.format(self.typ, item.name))
        list.append(self, item)


class LoggingSet(set):
    def __init__(self, typ, verbose):
        self.typ = typ
        self._verbose = verbose
        return set.__init__(self)

    def add(self, name):
        if self._verbose:
            print('use {0} "{1}"'.format(self.typ, name))
        set.add(self, name)
