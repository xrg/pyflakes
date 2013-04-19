"""
API for the command-line I{pyflakes} tool.
"""

import sys
import os
import _ast
from optparse import OptionParser

from pyflakes import checker, __version__
from pyflakes import reporter as modReporter
from pyflakes.messages import UnusedImport, UndefinedExport, UndefinedLocal, UndefinedName

__all__ = ['check', 'checkPath', 'checkRecursive', 'iterSourceCode', 'main']

allowed_undefines = ('_', 'openerp_version' )

def check(codeString, filename, reporter=None):
    """
    Check the Python source given by C{codeString} for flakes.

    @param codeString: The Python source to check.
    @type codeString: C{str}

    @param filename: The name of the file the source came from, used to report
        errors.
    @type filename: C{str}

    @param reporter: A L{Reporter} instance, where errors and warnings will be
        reported.

    @return: The number of warnings emitted.
    @rtype: C{int}
    """
    if reporter is None:
        reporter = modReporter._makeDefaultReporter()
    # First, compile into an AST and handle syntax errors.
    try:
        tree = compile(codeString, filename, "exec", _ast.PyCF_ONLY_AST)
    except SyntaxError:
        value = sys.exc_info()[1]
        msg = value.args[0]

        (lineno, offset, text) = value.lineno, value.offset, value.text

        # If there's an encoding problem with the file, the text is None.
        if text is None:
            # Avoid using msg, since for the only known case, it contains a
            # bogus message that claims the encoding the file declared was
            # unknown.
            reporter.unexpectedError(filename, 'problem decoding source')
        else:
            reporter.syntaxError(filename, msg, lineno, offset, text)
        return 1
    except Exception:
        value = sys.exc_info()[1]
        msg = value.args[0]
        reporter.unexpectedError(filename, 'problem decoding source: %s' % msg)
        return 1
    else:
        # Okay, it's syntactically valid.  Now check it.
        w = checker.Checker(tree, filename)
        w.messages.sort(key=lambda m: m.lineno)
        for warning in w.messages:
            # decide on the severity of each message:
            if filename.endswith('__init__.py') and isinstance(w, UnusedImport):
                pass
            elif isinstance(warning, UndefinedName) \
                        and warning.message_args[0] in allowed_undefines:
                # Some undefined names may be legal, such as gettext's "_()"
                reporter.flake(warning)
            elif isinstance(warning, (UndefinedExport, UndefinedLocal, UndefinedName)):
                # the code appears to be broken
                reporter.flake_error(warning)
            else:
                # a warning, the code could still work, eventually
                reporter.flake(warning)

        return len(w.messages)


def checkPath(filename, reporter=None):
    """
    Check the given path, printing out any warnings detected.

    @param reporter: A L{Reporter} instance, where errors and warnings will be
        reported.

    @return: the number of warnings printed
    """
    if reporter is None:
        reporter = modReporter._makeDefaultReporter()
    try:
        f = open(filename, 'U')
        try:
            return check(f.read() + '\n', filename, reporter)
        finally:
            f.close()
    except UnicodeError:
        reporter.unexpectedError(filename, 'problem decoding source')
    except IOError:
        msg = sys.exc_info()[1]
        reporter.unexpectedError(filename, msg.args[1])
    return 1


def iterSourceCode(paths):
    """
    Iterate over all Python source files in C{paths}.

    @param paths: A list of paths.  Directories will be recursed into and
        any .py files found will be yielded.  Any non-directories will be
        yielded as-is.
    """
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith('.py'):
                        yield os.path.join(dirpath, filename)
        else:
            yield path


def checkRecursive(paths, reporter):
    """
    Recursively check all source files in C{paths}.

    @param paths: A list of paths to Python source files and directories
        containing Python source files.
    @param reporter: A L{Reporter} where all of the warnings and errors
        will be reported to.
    @return: The number of warnings found.
    """
    warnings = 0
    for sourcePath in iterSourceCode(paths):
        warnings += checkPath(sourcePath, reporter)
    return warnings


def main(prog=None):
    parser = OptionParser(prog=prog, version=__version__)
    __, args = parser.parse_args()
    reporter = modReporter._makeDefaultReporter()
    if args:
        warnings = checkRecursive(args, reporter)
    else:
        warnings = check(sys.stdin.read(), '<stdin>', reporter)

    if reporter.numErrors:
        raise SystemExit(1)
    elif reporter.numWarnings:
        raise SystemExit(3)
    elif warnings:
        raise SystemExit(4)
    else:
        return
