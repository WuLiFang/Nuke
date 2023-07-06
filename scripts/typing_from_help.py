# -*- coding=UTF-8 -*-
"""generate typing from module help.  

Usage: "$PYTHON3" ./scripts/typing_from_help.py help.txt
"""

from __future__ import absolute_import, division, print_function, unicode_literals
from typing import Iterable, Iterator, List, Optional, Sequence, Text, Tuple
import cast_unknown as cast
import re
import ast

import logging


class _g:
    module_name = ""


_LOGGER = logging.getLogger(__name__)


_CLASS_MRO_START = "Method resolution order:"
_CLASS_METHODS_START = "Methods defined here:"
_CLASS_CLASS_METHODS_START = "Class methods defined here:"
_CLASS_STATIC_METHODS_START = "Static methods defined here:"
_CLASS_DATA_ATTR_START = "Data and other attributes defined here:"
_CLASS_READ_ONLY_PROPERTY_START = "Readonly properties defined here:"
_CLASS_DATA_DESC_START = "Data descriptors defined here:"
_CLASS_INHERITED_METHODS_START = "Methods inherited from (.+):"
_CLASS_INHERITED_CLASS_METHODS_START = "Class methods inherited from (.+):"
_CLASS_INHERITED_STATIC_METHODS_START = "Static methods inherited from (.+):"
_CLASS_INHERITED_DATA_ATTR_START = "Data and other attributes inherited from (.+):"
_CLASS_INHERITED_DATA_DESC_START = "Data descriptors inherited from (.+):"
_CLASS_INHERITED_READ_ONLY_PROPERTY_START = "Readonly properties inherited from (.+):"
_CLASS_SECTION_END = "-{20,}"

_TYPE_MAP = {
    "object": "",
    "exceptions.Exception": "Exception",
    "builtins.object": "object",
    "builtins.tuple": "tuple",
    "String": "typing.Text",
    "string": "typing.Text",
    "str": "typing.Text",
    "Float": "float",
    "Floating point value": "float",
    "Bool": "bool",
    "Boolean": "bool",
    "Int": "int",
    "Integer": "int",
    "integer": "int",
    "Integer value": "int",
    "void": "None",
    "list of strings or single string": "typing.Union[typing.List[typing.Text], typing.Text]",
    "List of strings": "typing.List[typing.Text]",
    "String list": "typing.List[typing.Text]",
    "[int]": "typing.List[int]",
    "List": "list",
    "(x, y, z)": "typing.Tuple[typing.Any, typing.Any, typing.Any]",
    "True or False": "bool",
}


def _iter_class_sections(lines):
    lines = iter(lines)
    section_type = "docstring"
    section_values = []
    for line in lines:
        if re.match(_CLASS_MRO_START, line):
            yield (section_type, section_values)
            section_type = "mro"
            section_values = []
        elif re.match(_CLASS_METHODS_START, line):
            yield (section_type, section_values)
            section_type = "methods"
            section_values = []
        elif re.match(_CLASS_STATIC_METHODS_START, line):
            yield (section_type, section_values)
            section_type = "static-methods"
            section_values = []
        elif re.match(_CLASS_CLASS_METHODS_START, line):
            yield (section_type, section_values)
            section_type = "class-methods"
            section_values = []
        elif re.match(_CLASS_DATA_ATTR_START, line):
            yield (section_type, section_values)
            section_type = "data"
            section_values = []
        elif re.match(_CLASS_DATA_DESC_START, line):
            yield (section_type, section_values)
            section_type = "data"
            section_values = []
        elif re.match(_CLASS_READ_ONLY_PROPERTY_START, line):
            yield (section_type, section_values)
            section_type = "data"
            section_values = []
        elif re.match(_CLASS_INHERITED_METHODS_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_METHODS_START, line)
            assert match
            section_type = "inherited-methods"
            section_values = [match.group(1)]
        elif re.match(_CLASS_INHERITED_CLASS_METHODS_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_CLASS_METHODS_START, line)
            assert match
            section_type = "inherited-class-methods"
            section_values = [match.group(1)]
        elif re.match(_CLASS_INHERITED_STATIC_METHODS_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_STATIC_METHODS_START, line)
            assert match
            section_type = "inherited-static-methods"
            section_values = [match.group(1)]
        elif re.match(_CLASS_INHERITED_DATA_ATTR_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_DATA_ATTR_START, line)
            assert match
            section_type = "inherited-data"
            section_values = [match.group(1)]
        elif re.match(_CLASS_INHERITED_DATA_DESC_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_DATA_DESC_START, line)
            assert match
            section_type = "inherited-data"
            section_values = [match.group(1)]
        elif re.match(_CLASS_INHERITED_READ_ONLY_PROPERTY_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_READ_ONLY_PROPERTY_START, line)
            assert match
            section_type = "inherited-data"
            section_values = [match.group(1)]
        elif re.match(_CLASS_SECTION_END, line):
            yield (section_type, section_values)
            section_type = ""
            section_values = []
        else:
            section_values.append(line)
    if section_values:
        yield (section_type, section_values)


def _strip_lines(lines):
    return "\n".join(lines).strip("\n").splitlines()


def _parse_by_indent(
    lines: Iterator[Text], indent="    "
) -> Iterator[Tuple[Text, Sequence[Text]]]:
    key = ""  # type: str
    values = []
    for line in lines:
        line = Text(line)
        if line.startswith(indent) or line == indent.rstrip(" "):
            values.append(line[len(indent) :])
        else:
            if key:
                yield (key, values)
                key = ""
                values = []
            key = line
    if values:
        yield (key, values)


def _parse_class_data(lines):
    for k, v in _parse_by_indent(lines):
        data_def = _parse_data_description(k)
        if v:
            data_def["docstring"] = _strip_lines(v)
        yield data_def


def _parse_type(s: Text) -> Text:
    s = _TYPE_MAP.get(s, s)
    if s.startswith("(") and s.endswith(")") and "," in s:
        return f"typing.Tuple[{s[1:-1]}]"
    if s.startswith("[") and s.endswith(""):
        return f"typing.Optional[{s[1:-1]}]"

    match = re.match(r"(?:an? )?(.+?) object$", s, re.I)
    if match:
        s = match.group(1)
    match = re.match(r"tuple of (.+?)(?:s| items| objects| instances)?$", s, re.I)
    if match:
        elem_type = _parse_type(match.group(1))
        if "," in elem_type:
            s = "typing.Tuple[%s]" % elem_type
        else:
            s = "typing.Tuple[%s, ...]" % elem_type
    match = re.match(r"list of (.+?)(?:s| items| objects| instances)?$", s, re.I)
    if match:
        s = f"typing.List[{_parse_type(match.group(1))}]"
    if _g.module_name and s.startswith(_g.module_name + "."):
        s = s[len(_g.module_name) + 1 :]
    return s


def _is_valid_arg_declaration(s: Text) -> bool:
    try:
        _ = ast.parse("def fn(%s):\n    pass" % s)
        return True
    except SyntaxError:
        return False


def _parse_args(s: Optional[Text]) -> Sequence[Text]:
    args = (s or "").split(",")
    args = [i.strip() for i in args]
    args = [_parse_type(i) for i in args]
    args = [i for i in args if i]
    if "..." in args:
        args = ["*args", "**kwargs"]

    b: List[Text] = []
    for i in args:
        match = re.match(r"\((.+)\)(.+)$", i)
        if match:
            b.append("%s: %s" % (match.group(2), match.group(1)))
            continue
        b.append(i)
    args = b
    b = []
    for i in args:
        if _is_valid_arg_declaration(i):
            b.append(i)
        elif _is_valid_type_expression(i):
            b.append("arg%d: %s" % (len(b) + 1, i))
        else:
            b.append("arg%d: typing.Literal['%s']" % (len(b) + 1, i))
    args = b
    return args


def _is_valid_type_expression(s: Text) -> bool:
    try:
        _ = ast.parse("var: %s = None" % s)
        return True
    except SyntaxError:
        return False


def _escape_python_string(s: Text) -> Text:
    return s.replace("\\", "\\\\")


def _is_valid_identifier(s: Text) -> bool:
    try:
        _ = ast.parse("def fn(%s: int = 1):\n    pass" % s)
        return True
    except SyntaxError:
        return False


class FunctionDeclaration:
    def __init__(
        self,
        name: Text = "",
        args: Sequence[Text] = (),
        return_type: Text = "",
        docstring: Sequence[Text] = (),
        inherits: Sequence[Text] = (),
        real_name: Text = "",
    ):
        self.name = name
        self.args = args
        self.return_type = return_type
        self.inherits = inherits
        self.real_name = real_name
        self.docstring = docstring


def _parse_function_docstring(fd: FunctionDeclaration, docstring: Sequence[Text]):
    doc_args: List[Text] = []
    doc_returns: List[Text] = []
    doc_overloads: List[Text] = []
    args = fd.args
    return_type = fd.return_type

    # handle `self.xxx() -> xxx:`
    b: List[Text] = []
    match_count = 0
    after_example = False
    for line in docstring:
        if not after_example:
            match = re.match(
                r"^\s*(?:self\.)?"
                + f"(?:{re.escape(_g.module_name)}\\.)?"
                + re.escape(fd.name)
                + r"\((.*?)\)(?: ?-> ?(.+?)\s*:?)?$",
                line,
            )
            if match:
                match_count += 1
                if match_count == 1:
                    args = _parse_args(match.group(1))
                    s = _parse_type(match.group(2) or "")
                    if _is_valid_type_expression(s):
                        return_type = s
                    elif s.startswith("returns "):
                        doc_returns.append(s[8:])
                    else:
                        b.append(s)
                else:
                    doc_overloads.append(line)
                continue
            after_example = re.match(".*example", line, re.I)
        b.append(line)
    docstring = b

    # handle @param, @return

    def _add_missing_newline(s: Iterable[Text]) -> Iterator[Text]:
        for i in s:
            for j in (
                i.replace("@param", "\n@param")
                .replace("@return", "\n@return")
                .split("\n")
            ):
                if j:
                    yield j

    b: List[Text] = []
    args_by_param: List[Text] = []
    for line in _add_missing_newline(docstring):
        match = re.match(r"^\s*@param(?: (.+?))?: (.+)$", line)
        if match:
            p_name, p_type = match.groups()
            p_name = (p_name or p_type.strip("").split(" ")[0]).strip()
            p_type = _parse_type(p_type)
            if not _is_valid_identifier(p_name):
                p_name = "param%d" % (len(args_by_param) + 1)
            arg = "%s: %s" % (p_name, p_type)
            if p_name == p_type or not _is_valid_arg_declaration(arg):
                arg = p_name
            args_by_param.append(arg)
            doc_args.append("%s: %s" % (p_name, p_type))
            continue
        match = re.match(r"^\s*@return(?:\s*:)? (.+)$", line)
        if match:
            s = _parse_type(match.group(1))
            if _is_valid_type_expression(s):
                assert fd.return_type == "", line
                return_type = s
            else:
                doc_returns.append(match.group(1))
            continue
        b.append(line)
    docstring = b
    if not args:
        args = args_by_param

    args = [i.strip() for i in args]
    args = [i for i in args if i]
    return_type = _parse_type(return_type)
    if return_type and not _is_valid_type_expression(return_type):
        _LOGGER.debug("ignore invalid type expiression: '%s'", return_type)
        doc_returns.append(return_type)
        return_type = ""
    docstring = _strip_lines(docstring)
    if doc_args:
        docstring = [*docstring, "", "Args:", *["    " + i for i in doc_args]]
    if doc_returns:
        docstring = [*docstring, "", "Returns:", *["    " + i for i in doc_returns]]
    if doc_overloads:
        docstring = [
            *docstring,
            "",
            "Overloads:",
            *["    " + i for i in doc_overloads],
        ]
    fd.args = args
    fd.return_type = return_type
    fd.docstring = (*fd.docstring, *docstring)


def _parse_class_method(lines) -> Iterator[FunctionDeclaration]:
    for k, v in _parse_by_indent(lines):
        match = re.match(r"^(.+?)(?:\((.+)\))?(?: from (.+))?$", k)
        if not match:
            raise NotImplementedError(k, v)
        docstring = v
        fd = FunctionDeclaration(name=match.group(1), args=_parse_args(match.group(2)))
        if "=" in fd.name:
            fd.name, alias = (i.strip() for i in fd.name.split("="))
            docstring = ["alias of %s" % alias, *docstring]

        _parse_function_docstring(fd, docstring)
        yield fd


def _iter_classes(lines):
    for class_key, class_values in _parse_by_indent(lines, " |  "):

        if not class_values:
            # Ignore summary list and empty lines
            continue

        match = re.match(r"(.+?) = class (.+?)(?:\((.+)\))?$", class_key)
        if match:
            g3 = match.group(3)
            yield dict(
                name=match.group(1),
                inherits=g3.split(",") if g3 else [],
                real_name=match.group(2),
            )
            continue
        match = re.match(r"class (.+?)(?:\((.+)\))?$", class_key)
        if not match:
            raise NotImplementedError(
                "_iter_classes: %s: %s" % (class_key, class_values)
            )
        g2 = match.group(2)
        class_def = dict(
            name=match.group(1),
            inherits=g2.split(",") if g2 else [],
            static_methods=[],
            class_methods=[],
            methods=[],
            data=[],
            docstring=[],
        )
        for (section_key, section_values) in _iter_class_sections(class_values):
            if section_key == "" and section_values == []:
                continue
            elif section_key == "inherited-data":
                continue
            elif section_key == "inherited-methods":
                continue
            elif section_key == "inherited-class-methods":
                continue
            elif section_key == "inherited-static-methods":
                continue
            elif section_key == "mro":
                continue
            elif section_key == "docstring":
                class_def["docstring"] = section_values
            elif section_key == "data":
                class_def["data"] = list(_parse_class_data(section_values))
            elif section_key == "methods":
                class_def["methods"] = list(_parse_class_method(section_values))
            elif section_key == "static-methods":
                class_def["static_methods"] = list(_parse_class_method(section_values))
            elif section_key == "class-methods":
                class_def["class_methods"] = list(_parse_class_method(section_values))
            else:
                raise NotImplementedError(section_key, section_values)
        class_def["docstring"] = _strip_lines(class_def["docstring"])
        yield class_def


def _iter_functions(lines) -> Iterator[FunctionDeclaration]:
    for k, v in _parse_by_indent(lines):
        match = re.match(r"(.+?) = (.+?)(?:\((.+)\))?$", k)
        if match:
            g3 = match.group(3)
            yield FunctionDeclaration(
                name=match.group(1),
                inherits=g3.split(",") if g3 else [],
                real_name=match.group(2),
            )
            continue

        match = re.match(r"(.+?) lambda (.*)$", k)
        if match:
            yield FunctionDeclaration(
                name=match.group(1),
                args=_parse_args(match.group(2)),
                docstring=_strip_lines(v),
                return_type="",
            )
            continue

        match = re.match(r"(.+?)\((.*)\)$", k)
        if not match:
            raise NotImplementedError(k, v)
        name = match.group(1)
        args = _parse_args(match.group(2))
        docstring = _strip_lines(v)
        fd = FunctionDeclaration(name=name, args=args)
        _parse_function_docstring(fd, docstring)
        yield fd


def _typing_from_class(class_def):
    name = class_def["name"]
    real_name = class_def.get("real_name")
    if real_name is not None:
        yield "%s = %s" % (name, real_name)
        return
    docstring = class_def["docstring"]
    inherits = class_def["inherits"]
    inherits = [_parse_type(i) for i in inherits]
    inherits = [i for i in inherits if i]
    methods: Sequence[FunctionDeclaration] = class_def["methods"]
    class_methods: Sequence[FunctionDeclaration] = class_def["class_methods"]
    static_methods: Sequence[FunctionDeclaration] = class_def["static_methods"]
    data = class_def["data"]
    yield "class %s%s:" % (name, "(%s)" % ",".join(inherits) if inherits else "")
    if docstring:
        yield '    """'
        for i in docstring:
            yield ("    %s" % i).rstrip()
        yield '    """'
        yield ""
    if data:
        for i in data:
            yield "    %s: %s%s" % (
                i["name"],
                i["value_type"],
                " = %s" % i["value"] if i["value"] else "",
            )
            if i["docstring"]:
                yield '    """'
                for j in i["docstring"]:
                    yield ("    %s" % j).rstrip()
                yield '    """'
            yield ""
    if static_methods:
        for i in static_methods:
            yield "    @staticmethod"
            yield "    def %s(%s)%s:" % (
                i.name,
                ", ".join(i.args),
                " -> %s" % i.return_type if i.return_type else "",
            )
            yield '        """'
            for j in i.docstring:
                yield ("        %s" % _escape_python_string(j)).rstrip()
            yield '        """'
            yield "        ..."
            yield ""
    if class_methods:
        for i in class_methods:
            if "cls" not in i.args:
                i.args = ("cls", *i.args)
            yield "    @classmethod"
            yield "    def %s(%s)%s:" % (
                i.args,
                ", ".join(i.args),
                " -> %s" % i.return_type if i.return_type else "",
            )
            yield '        """'
            for j in i.docstring:
                yield ("        %s" % _escape_python_string(j)).rstrip()
            yield '        """'
            yield "        ..."
            yield ""
    if methods:
        for i in methods:
            if "self" not in i.args:
                i.args = ("self", *i.args)
            yield "    def %s(%s)%s:" % (
                i.name,
                ", ".join(i.args),
                " -> %s" % i.return_type if i.return_type else "",
            )
            yield '        """'
            for j in i.docstring:
                yield ("        %s" % _escape_python_string(j)).rstrip()
            yield '        """'
            yield "        ..."
            yield ""

    yield "    ..."


def _typing_from_function(func_def: FunctionDeclaration):
    name = func_def.name
    real_name = func_def.real_name
    if real_name:
        yield "%s = %s" % (name, real_name)
        return
    args = func_def.args
    return_type = func_def.return_type
    docstring = func_def.docstring
    yield "def %s(%s)%s:" % (
        name,
        ", ".join(args),
        " -> %s" % return_type if return_type else "",
    )
    yield '    """'
    for i in docstring:
        yield ("    %s" % _escape_python_string(i)).rstrip()
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


def _remove_prefix(s: Text, prefix: Text) -> Text:
    if s.startswith(prefix):
        return s[len(prefix) :]
    return s


def _parse_data_description(i):
    match = re.match(r"^(.+?)(?: ?= ?(.+))?$", i)
    if not match:
        raise NotImplementedError(i)
    name = match.group(1)
    value = match.group(2) or ""
    value_type = "..."
    if _is_valid_type_expression(value):
        value_type = _remove_prefix(value, _g.module_name + ".")
    docstring = []
    if value.endswith("..."):
        docstring.append(value)
    elif value.startswith("<"):
        docstring.append(value)
    elif value.startswith(("'", '"')):
        docstring.append(value)
        value_type = "typing.Text"
    elif value.startswith("["):
        docstring.append(value)
        value_type = "list"
    elif value.startswith("{"):
        docstring.append(value)
        value_type = "dict"
    elif value in ("True", "False"):
        docstring.append(value)
        value_type = "bool"
    elif re.match(r"^-?\d+", value):
        value_type = "int"
        if "." in value:
            value_type = "float"
    if not _is_valid_type_expression(value_type):
        _LOGGER.warning("ignore invalid type: %s", value_type)
        value_type = "..."
    return dict(name=name, value=value, value_type=value_type, docstring=docstring)


def _iter_data(lines):
    for i in lines:
        if i == "":
            continue
        yield _parse_data_description(i)


def _typing_from_datum(datum_def):
    name = datum_def["name"]
    value = datum_def["value"]
    value_type = datum_def["value_type"]
    docstring = datum_def["docstring"]

    yield "%s: %s%s" % (name, value_type, " = %s" % value if value else "")
    if docstring:
        yield '"""'
        for i in docstring:
            yield _escape_python_string(i)
        yield '"""'


def _typing_from_data(lines):
    for i in _iter_data(lines):
        for j in _typing_from_datum(i):
            yield j
        yield ""


def _handle_windows_line_ending(lines):
    for i in lines:
        i = Text(i)
        yield i.strip("\r\n")


def iterate_typing_from_help(lines):
    yield "# -*- coding=UTF-8 -*-"
    yield "# This typing file was generated by typing_from_help.py"
    yield "# pyright: reportUndefinedVariable=information,reportUnusedImport=false"
    for k, v in _parse_by_indent(lines):
        if k == "NAME":
            yield '"""'
            for i in v:
                yield i
            yield '"""'
            yield ""
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
        elif k == "DESCRIPTION":
            yield '"""'
            for i in v:
                yield i
            yield '"""'
        elif k == "SUBMODULES":
            for i in v:
                yield "from . import %s" % i
        elif k == "VERSION":
            yield "# version: %s" % cast.one(v)
        elif k == "FUNCTIONS":
            for i in _typing_from_functions(v):
                yield i
        elif not v:
            pass
        else:
            raise NotImplementedError(k, v)


def typing_from_help(text):
    return "\n".join(iterate_typing_from_help(Text(text).splitlines()))


if __name__ == "__main__":
    import argparse
    import sys
    import codecs

    parser = argparse.ArgumentParser()
    _ = parser.add_argument("--type", dest="type")
    _ = parser.add_argument("--module", dest="module", default="")
    _ = parser.add_argument("file")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    should_close = False
    _g.module_name = args.module
    if args.file == "-":
        f = sys.stdin
    else:
        f = codecs.open(args.file, "r", encoding="utf-8")
        should_close = True

    try:
        lines = _handle_windows_line_ending(f)
        if args.type == "class":
            for i in _typing_from_classes(lines):
                print(i)
        else:
            for i in iterate_typing_from_help(lines):
                print(i)
    finally:
        if should_close:
            f.close()
