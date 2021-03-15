# -*- coding=UTF-8 -*-
"""generate typing from module help.  

Usage: "$NUKE_PYTHON" -c 'import nuke; import _nuke; help(_nuke)' | "$PYTHON27" ./scripts/typing_from_help.py -
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from sys import stderr
import six
import cast_unknown as cast
import re


_CLASS_MRO_START = 'Method resolution order:'
_CLASS_METHODS_START = 'Methods defined here:'
_CLASS_DATA_ATTR_START = 'Data and other attributes defined here:'
_CLASS_DATA_DESC_START = 'Data descriptors defined here:'
_CLASS_INHERITED_METHODS_START = 'Methods inherited from (.+):'
_CLASS_INHERITED_DATA_ATTR_START = 'Data and other attributes inherited from (.+):'
_CLASS_INHERITED_DATA_DESC_START = 'Data descriptors inherited from (.+):'
_CLASS_SECTION_END = '-{20,}'

TYPE_MAP = {
    "__builtin__.object": "",
    "__builtin__.Knob": "",
    "object": "",
    "exceptions.Exception": "Exception",
    "String": "six.binary_type",
    "string": "six.binary_type",
    "str": "six.binary_type",
    "Float": "float",
    "Floating point value": "float",
    "Bool": "bool",
    "Boolean": "bool",
    "Integer": "int",
    "integer": "int",
    "Integer value": "int",
    "void": "None",
    "list of strings or single string": "typing.Union[typing.List[six.binary_type], six.binary_type]",
    "List of strings": "typing.List[six.binary_type]",
    "list of str": "typing.List[six.binary_type]",
    "String list": "typing.List[six.binary_type]",
    "List of int": "typing.List[int]",
    "list of int": "typing.List[int]",
    "[int]": "typing.List[int]",
    "List": 'list',
    "(x, y, z)": 'typing.Tuple',
    "list of (x,y,z) tuples": 'typing.List',
}


def _iter_class_sections(lines):
    lines = iter(lines)
    section_type = 'docstring'
    section_values = []
    for line in lines:
        if re.match(_CLASS_MRO_START, line):
            yield (section_type, section_values)
            section_type = 'mro'
            section_values = []
        elif re.match(_CLASS_METHODS_START, line):
            yield (section_type, section_values)
            section_type = 'methods'
            section_values = []
        elif re.match(_CLASS_DATA_ATTR_START, line):
            yield (section_type, section_values)
            section_type = 'data'
            section_values = []
        elif re.match(_CLASS_DATA_DESC_START, line):
            yield (section_type, section_values)
            section_type = 'data'
            section_values = []
        elif re.match(_CLASS_INHERITED_METHODS_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_METHODS_START, line)
            section_type = 'inherited-methods'
            section_values = [match.group(1)]
        elif re.match(_CLASS_INHERITED_DATA_ATTR_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_DATA_ATTR_START, line)
            section_type = 'inherited-data'
            section_values = [match.group(1)]
        elif re.match(_CLASS_INHERITED_DATA_DESC_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_DATA_DESC_START, line)
            section_type = 'inherited-data'
            section_values = [match.group(1)]
        elif re.match(_CLASS_SECTION_END, line):
            yield (section_type, section_values)
            section_type = ''
            section_values = []
        else:
            section_values.append(line)
    if section_values:
        yield (section_type, section_values)


def _strip_lines(lines):
    return "\n".join(lines).strip("\n").splitlines()


def _parse_by_indent(lines, indent='    '):
    key = ''
    values = []
    for line in lines:
        line = cast.text(line)
        if line.startswith(indent):
            values.append(line[len(indent):])
        else:
            if values:
                yield (key, values)
                values = []
            key = line
    if values:
        yield (key, values)


def _parse_class_data(lines):
    for k, v in _parse_by_indent(
            lines
    ):
        match = re.match(r"^(.+?)(?: ?= ?(.+))?$", k)
        if not match:
            raise NotImplementedError(k, v)
        name = match.group(1)
        value = match.group(2) or ""
        if value.startswith("<") and value.endswith(">"):
            value = ""
        yield dict(
            name=name,
            value=value,
            docstring=_strip_lines(v),

        )


def _parse_args(args):
    args = (args or "").split(",")
    args = [i.strip() for i in args]
    args = [TYPE_MAP.get(i, i) for i in args]
    args = [i for i in args if i]
    if "..." in args:
        args = ["*args", "**kwargs"]

    ret = []
    for i in args:
        match = re.match(r"\((.+)\)(.+)$", i)
        if match:
            ret.append("%s: %s" % (match.group(2), match.group(1)))
            continue
        ret.append(i)

    return ret


def _parse_class_method(lines):
    for k, v in _parse_by_indent(
            lines
    ):
        match = re.match(r"^(.+?)(?:\((.+)\))?$", k)
        if not match:
            raise NotImplementedError(k, v)
        name = match.group(1)
        args = _parse_args(match.group(2))
        docstring = v
        return_type = ""
        match = len(v[0]) > 0 and re.match(
            r"(?:self\.)?" +
            re.escape(name) +
            r"\((.*)\) ?-> ?(.+?)\.? *:?$",
            v[0]) or None
        if match:
            docstring = docstring[1:]
            args = _parse_args(match.group(1))
            return_type = match.group(2) or ""
        args = [i.strip() for i in args]
        args = [TYPE_MAP.get(i, i) for i in args]
        args = [i for i in args if i]
        if "self" not in args:
            args.insert(0, "self")
        return_type = TYPE_MAP.get(return_type, return_type)
        docstring = _strip_lines(docstring)

        yield dict(
            name=name,
            args=args,
            return_type=return_type,
            docstring=docstring,
        )


def _iter_classes(lines):
    for class_key, class_values in _parse_by_indent(
            lines,
            " |  "):

        if not class_values:
            # Ignore summary list and empty lines
            continue
        match = re.match(r"class (.+?)(?:\((.+)\))?$", class_key)
        if not match:
            raise NotImplementedError("class: %s: %s" %
                                      (class_key, class_values))
        g2 = match.group(2)
        class_def = dict(
            name=match.group(1),
            inherits=g2.split(",") if g2 else [],
            methods=[],
            data=[],
            docstring=[],
        )
        for (section_key, section_values) in _iter_class_sections(class_values):
            if section_key == '' and section_values == []:
                continue
            elif section_key == 'inherited-data':
                continue
            elif section_key == 'inherited-methods':
                continue
            elif section_key == 'mro':
                continue
            elif section_key == 'docstring':
                class_def["docstring"] = section_values
            elif section_key == 'data':
                class_def["data"] = list(_parse_class_data(
                    section_values
                ))
            elif section_key == 'methods':
                class_def["methods"] = list(_parse_class_method(
                    section_values
                ))
            else:
                raise NotImplementedError(section_key, section_values)
        class_def["docstring"] = _strip_lines(class_def["docstring"])
        yield class_def


def _iter_functions(lines):
    for k, v in _parse_by_indent(lines):
        match = re.match(r"(.+?)\((.*)\)$", k)
        if not match:
            raise NotImplementedError(k, v)
        name = match.group(1)
        args = _parse_args(match.group(2))
        docstring = _strip_lines(v)
        match = len(docstring[0]) > 0 and re.match(
            re.escape(name) +
            r"\((.*)\) ?-> ?(.+?)\.? *$",
            docstring[0]) or None
        return_type = ""
        if match:
            docstring = docstring[1:]
            args = _parse_args(match.group(1))
            return_type = match.group(2) or ""
        return_type = TYPE_MAP.get(return_type, return_type)
        docstring = _strip_lines(docstring)
        yield dict(
            name=name,
            args=args,
            docstring=docstring,
            return_type=return_type
        )


def _typing_from_class(class_def):
    name = class_def["name"]
    docstring = class_def["docstring"]
    inherits = class_def["inherits"]
    inherits = [TYPE_MAP.get(i, i) for i in inherits]
    inherits = [i for i in inherits if i]
    methods = class_def["methods"]
    data = class_def["data"]
    yield "class %s%s:" % (name, "(%s)" % ",".join(inherits) if inherits else "")
    if docstring:
        yield '    """'
        for i in docstring:
            yield "    %s" % i
        yield '    """'
        yield ""
    if data:
        for i in data:
            yield "    %s: ...%s" % (i["name"], " = %s" % i["value"] if i['value'] else '')
            yield '    """'
            for j in i["docstring"]:
                yield "    %s" % j
            yield '    """'
            yield ""
    if methods:
        for i in methods:
            yield "    def %s(%s)%s:" % (i["name"], ", ".join(i["args"]), " -> %s" % i["return_type"] if i["return_type"] else "")
            yield '        """'
            for j in i["docstring"]:
                yield "        %s" % j
            yield '        """'
            yield "        ..."
            yield ""

    yield "    ..."


def _typing_from_function(func_def):
    name = func_def["name"]
    args = func_def["args"]
    return_type = func_def["return_type"]
    docstring = func_def["docstring"]
    yield "def %s(%s)%s:" % (name, ", ".join(args), " -> %s" % return_type if return_type else "")
    yield '    """'
    for i in docstring:
        yield "    %s" % i
    yield '    """'
    yield "    ..."
    yield ""


def _typing_from_functions(lines):
    for i in _iter_functions(lines):
        for j in _typing_from_function(i):
            yield j
        yield ""


def _typing_from_classes(lines):
    for i in _iter_classes(lines):
        for j in _typing_from_class(i):
            yield j
        yield ""


def _iter_data(lines):
    for i in lines:
        if i == "":
            continue
        match = re.match(r"(.+?) ?= ?(.+)$", i)
        if not match:
            raise NotImplementedError(i)
        name = match.group(1)
        value = match.group(2)
        value_type = '...'
        if value.endswith("..."):
            value = ''
        elif value.startswith("<"):
            value = ''
        elif value.startswith(("'", '"')):
            value_type = "six.binary_type"
            value = ''
        elif value.startswith("["):
            value = ''
            value_type = 'list'
        elif value.startswith("{"):
            value = ''
            value_type = 'dict'
        elif value in ('True', 'False'):
            value = ''
            value_type = 'bool'
        elif re.match(r"-?\d+", value):
            value_type = 'int'
        yield dict(
            name=name,
            value=value,
            value_type=value_type,
        )


def _typing_from_datum(datum_def):
    name = datum_def["name"]
    value = datum_def["value"]
    value_type = datum_def["value_type"]

    yield "%s: %s%s" % (name, value_type, " = %s" % value if value else "")


def _typing_from_data(lines):
    for i in _iter_data(lines):
        for j in _typing_from_datum(i):
            yield j
        yield ""


def _fix_nuke_docstring(lines):
    for i in lines:
        i = cast.text(i)
        if i.startswith("       rief "):
            yield "        "+i[12:]
            continue
        yield i


def _handle_windows_line_ending(lines):
    for i in lines:
        i = cast.text(i)
        yield i.strip("\n")


def iterate_typing_from_help(lines):
    yield "# -*- coding=UTF-8 -*-"
    yield "# This typing file was generated by typing_from_help.py"
    for k, v in _parse_by_indent(_fix_nuke_docstring(_handle_windows_line_ending(lines)),):
        if k == "NAME":
            yield '"""'
            for i in v:
                yield i
            yield '"""'
            yield ""
            yield "import six"
            yield "import typing"
            yield ""
        elif k == "DATA":
            for i in _typing_from_data(v):
                yield i
        elif k == "CLASSES":
            for i in _typing_from_classes(v):
                yield i
        elif k == "FILE":
            pass
        elif k == "PACKAGE CONTENTS":
            pass
        elif k == "FUNCTIONS":
            for i in _typing_from_functions(v):
                yield i
        else:
            raise NotImplementedError(k, v)


def typing_from_help(text):
    return "\n".join(iterate_typing_from_help(cast.text(text).splitlines()))


if __name__ == '__main__':
    import fileinput
    import argparse
    import sys
    import codecs

    parser = argparse.ArgumentParser()
    parser.add_argument("--type", dest="type")
    parser.add_argument("file")
    args = parser.parse_args()
    should_close = False
    if args.file == '-':
        f = sys.stdin
    else:
        f = codecs.open(args.file, "r", encoding="utf-8")
        should_close = True

    try:
        if args.type == 'class':
            for i in _typing_from_classes(f):
                print(i)
        else:
            for i in iterate_typing_from_help(f):
                print(i)
    finally:
        if should_close:
            f.close()
