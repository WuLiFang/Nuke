# -*- coding=UTF-8 -*-
# This typing file was generated by typing_from_help.py
"""
Qt.QtXmlPatterns
"""

import six
import typing

class QAbstractMessageHandler(PySide.QtCore.QObject):
    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    staticMetaObject: ...
    """
    <PySide.QtCore.QMetaObject object>
    """

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def handleMessage(self, *args, **kwargs):
        """
        """
        ...

    def message(self, *args, **kwargs):
        """
        """
        ...

    ...

class QAbstractUriResolver(PySide.QtCore.QObject):
    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    staticMetaObject: ...
    """
    <PySide.QtCore.QMetaObject object>
    """

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def resolve(self, *args, **kwargs):
        """
        """
        ...

    ...

class QAbstractXmlNodeModel(Shiboken.Object):
    FirstChild: ...
    """
    PySide.QtXmlPatterns.QAbstractXmlNodeModel.SimpleAxis.Fir...
    """

    InheritNamespaces: ...
    """
    PySide.QtXmlPatterns.QAbstractXmlNodeModel.NodeCop...
    """

    NextSibling: ...
    """
    PySide.QtXmlPatterns.QAbstractXmlNodeModel.SimpleAxis.Ne...
    """

    NodeCopySetting: ...
    """
    <type 'PySide.QtXmlPatterns.QAbstractXmlNodeModel.No...
    """

    Parent: ... = PySide.QtXmlPatterns.QAbstractXmlNodeModel.SimpleAxis.Parent
    """
    """

    PreserveNamespaces: ...
    """
    PySide.QtXmlPatterns.QAbstractXmlNodeModel.NodeCo...
    """

    PreviousSibling: ...
    """
    PySide.QtXmlPatterns.QAbstractXmlNodeModel.SimpleAxi...
    """

    SimpleAxis: ...
    """
    <type 'PySide.QtXmlPatterns.QAbstractXmlNodeModel.SimpleA...
    """

    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def attributes(self, *args, **kwargs):
        """
        """
        ...

    def baseUri(self, *args, **kwargs):
        """
        """
        ...

    def compareOrder(self, *args, **kwargs):
        """
        """
        ...

    def createIndex(self, *args, **kwargs):
        """
        """
        ...

    def documentUri(self, *args, **kwargs):
        """
        """
        ...

    def elementById(self, *args, **kwargs):
        """
        """
        ...

    def isDeepEqual(self, *args, **kwargs):
        """
        """
        ...

    def kind(self, *args, **kwargs):
        """
        """
        ...

    def name(self, *args, **kwargs):
        """
        """
        ...

    def namespaceBindings(self, *args, **kwargs):
        """
        """
        ...

    def namespaceForPrefix(self, *args, **kwargs):
        """
        """
        ...

    def nextFromSimpleAxis(self, *args, **kwargs):
        """
        """
        ...

    def nodesByIdref(self, *args, **kwargs):
        """
        """
        ...

    def root(self, *args, **kwargs):
        """
        """
        ...

    def sendNamespaces(self, *args, **kwargs):
        """
        """
        ...

    def sourceLocation(self, *args, **kwargs):
        """
        """
        ...

    def stringValue(self, *args, **kwargs):
        """
        """
        ...

    def typedValue(self, *args, **kwargs):
        """
        """
        ...

    ...

class QAbstractXmlReceiver(Shiboken.Object):
    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def atomicValue(self, *args, **kwargs):
        """
        """
        ...

    def attribute(self, *args, **kwargs):
        """
        """
        ...

    def characters(self, *args, **kwargs):
        """
        """
        ...

    def comment(self, *args, **kwargs):
        """
        """
        ...

    def endDocument(self, *args, **kwargs):
        """
        """
        ...

    def endElement(self, *args, **kwargs):
        """
        """
        ...

    def endOfSequence(self, *args, **kwargs):
        """
        """
        ...

    def namespaceBinding(self, *args, **kwargs):
        """
        """
        ...

    def processingInstruction(self, *args, **kwargs):
        """
        """
        ...

    def startDocument(self, *args, **kwargs):
        """
        """
        ...

    def startElement(self, *args, **kwargs):
        """
        """
        ...

    def startOfSequence(self, *args, **kwargs):
        """
        """
        ...

    def whitespaceOnly(self, *args, **kwargs):
        """
        """
        ...

    ...

class QSourceLocation(Shiboken.Object):
    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    def __copy__(self, *args, **kwargs):
        """
        """
        ...

    def __eq__(self, *args, **kwargs):
        """
        x.__eq__(y) <==> x==y
        """
        ...

    def __ge__(self, *args, **kwargs):
        """
        x.__ge__(y) <==> x>=y
        """
        ...

    def __gt__(self, *args, **kwargs):
        """
        x.__gt__(y) <==> x>y
        """
        ...

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def __le__(self, *args, **kwargs):
        """
        x.__le__(y) <==> x<=y
        """
        ...

    def __lt__(self, *args, **kwargs):
        """
        x.__lt__(y) <==> x<y
        """
        ...

    def __ne__(self, *args, **kwargs):
        """
        x.__ne__(y) <==> x!=y
        """
        ...

    def __nonzero__(self, *args, **kwargs):
        """
        x.__nonzero__() <==> x != 0
        """
        ...

    def __repr__(self, *args, **kwargs):
        """
        x.__repr__() <==> repr(x)
        """
        ...

    def column(self, *args, **kwargs):
        """
        """
        ...

    def isNull(self, *args, **kwargs):
        """
        """
        ...

    def line(self, *args, **kwargs):
        """
        """
        ...

    def setColumn(self, *args, **kwargs):
        """
        """
        ...

    def setLine(self, *args, **kwargs):
        """
        """
        ...

    def setUri(self, *args, **kwargs):
        """
        """
        ...

    def uri(self, *args, **kwargs):
        """
        """
        ...

    ...

class QXmlFormatter(QXmlSerializer):
    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def atomicValue(self, *args, **kwargs):
        """
        """
        ...

    def attribute(self, *args, **kwargs):
        """
        """
        ...

    def characters(self, *args, **kwargs):
        """
        """
        ...

    def comment(self, *args, **kwargs):
        """
        """
        ...

    def endDocument(self, *args, **kwargs):
        """
        """
        ...

    def endElement(self, *args, **kwargs):
        """
        """
        ...

    def endOfSequence(self, *args, **kwargs):
        """
        """
        ...

    def indentationDepth(self, *args, **kwargs):
        """
        """
        ...

    def processingInstruction(self, *args, **kwargs):
        """
        """
        ...

    def setIndentationDepth(self, *args, **kwargs):
        """
        """
        ...

    def startDocument(self, *args, **kwargs):
        """
        """
        ...

    def startElement(self, *args, **kwargs):
        """
        """
        ...

    def startOfSequence(self, *args, **kwargs):
        """
        """
        ...

    ...

class QXmlItem(Shiboken.Object):
    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    def __copy__(self, *args, **kwargs):
        """
        """
        ...

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def __nonzero__(self, *args, **kwargs):
        """
        x.__nonzero__() <==> x != 0
        """
        ...

    def isAtomicValue(self, *args, **kwargs):
        """
        """
        ...

    def isNode(self, *args, **kwargs):
        """
        """
        ...

    def isNull(self, *args, **kwargs):
        """
        """
        ...

    def toAtomicValue(self, *args, **kwargs):
        """
        """
        ...

    def toNodeModelIndex(self, *args, **kwargs):
        """
        """
        ...

    ...

class QXmlName(Shiboken.Object):
    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    @staticmethod
    def fromClarkName(*args, **kwargs):
        """
        """
        ...

    @staticmethod
    def isNCName(*args, **kwargs):
        """
        """
        ...

    def __copy__(self, *args, **kwargs):
        """
        """
        ...

    def __eq__(self, *args, **kwargs):
        """
        x.__eq__(y) <==> x==y
        """
        ...

    def __ge__(self, *args, **kwargs):
        """
        x.__ge__(y) <==> x>=y
        """
        ...

    def __gt__(self, *args, **kwargs):
        """
        x.__gt__(y) <==> x>y
        """
        ...

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def __le__(self, *args, **kwargs):
        """
        x.__le__(y) <==> x<=y
        """
        ...

    def __lt__(self, *args, **kwargs):
        """
        x.__lt__(y) <==> x<y
        """
        ...

    def __ne__(self, *args, **kwargs):
        """
        x.__ne__(y) <==> x!=y
        """
        ...

    def __nonzero__(self, *args, **kwargs):
        """
        x.__nonzero__() <==> x != 0
        """
        ...

    def isNull(self, *args, **kwargs):
        """
        """
        ...

    def localName(self, *args, **kwargs):
        """
        """
        ...

    def namespaceUri(self, *args, **kwargs):
        """
        """
        ...

    def prefix(self, *args, **kwargs):
        """
        """
        ...

    def toClarkName(self, *args, **kwargs):
        """
        """
        ...

    ...

class QXmlNamePool(Shiboken.Object):
    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    def __copy__(self, *args, **kwargs):
        """
        """
        ...

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    ...

class QXmlNodeModelIndex(Shiboken.Object):
    Attribute: ... = PySide.QtXmlPatterns.QXmlNodeModelIndex.NodeKind.Attribute
    """
    """

    Comment: ... = PySide.QtXmlPatterns.QXmlNodeModelIndex.NodeKind.Comment
    """
    """

    Document: ... = PySide.QtXmlPatterns.QXmlNodeModelIndex.NodeKind.Document
    """
    """

    DocumentOrder: ...
    """
    <type 'PySide.QtXmlPatterns.QXmlNodeModelIndex.Documen...
    """

    Element: ... = PySide.QtXmlPatterns.QXmlNodeModelIndex.NodeKind.Element
    """
    """

    Follows: ...
    """
    PySide.QtXmlPatterns.QXmlNodeModelIndex.DocumentOrder.Follow...
    """

    Is: ... = PySide.QtXmlPatterns.QXmlNodeModelIndex.DocumentOrder.Is
    """
    """

    Namespace: ... = PySide.QtXmlPatterns.QXmlNodeModelIndex.NodeKind.Namespace
    """
    """

    NodeKind: ...
    """
    <type 'PySide.QtXmlPatterns.QXmlNodeModelIndex.NodeKind'>
    """

    Precedes: ...
    """
    PySide.QtXmlPatterns.QXmlNodeModelIndex.DocumentOrder.Prece...
    """

    ProcessingInstruction: ...
    """
    PySide.QtXmlPatterns.QXmlNodeModelIndex.NodeKi...
    """

    Text: ... = PySide.QtXmlPatterns.QXmlNodeModelIndex.NodeKind.Text
    """
    """

    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    def __copy__(self, *args, **kwargs):
        """
        """
        ...

    def __eq__(self, *args, **kwargs):
        """
        x.__eq__(y) <==> x==y
        """
        ...

    def __ge__(self, *args, **kwargs):
        """
        x.__ge__(y) <==> x>=y
        """
        ...

    def __gt__(self, *args, **kwargs):
        """
        x.__gt__(y) <==> x>y
        """
        ...

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def __le__(self, *args, **kwargs):
        """
        x.__le__(y) <==> x<=y
        """
        ...

    def __lt__(self, *args, **kwargs):
        """
        x.__lt__(y) <==> x<y
        """
        ...

    def __ne__(self, *args, **kwargs):
        """
        x.__ne__(y) <==> x!=y
        """
        ...

    def __nonzero__(self, *args, **kwargs):
        """
        x.__nonzero__() <==> x != 0
        """
        ...

    def additionalData(self, *args, **kwargs):
        """
        """
        ...

    def data(self, *args, **kwargs):
        """
        """
        ...

    def internalPointer(self, *args, **kwargs):
        """
        """
        ...

    def isNull(self, *args, **kwargs):
        """
        """
        ...

    def model(self, *args, **kwargs):
        """
        """
        ...

    ...

class QXmlQuery(Shiboken.Object):
    QueryLanguage: ...
    """
    <type 'PySide.QtXmlPatterns.QXmlQuery.QueryLanguage'>
    """

    XPath20: ... = PySide.QtXmlPatterns.QXmlQuery.QueryLanguage.XPath20
    """
    """

    XQuery10: ... = PySide.QtXmlPatterns.QXmlQuery.QueryLanguage.XQuery10
    """
    """

    XSLT20: ... = PySide.QtXmlPatterns.QXmlQuery.QueryLanguage.XSLT20
    """
    """

    XmlSchema11IdentityConstraintField: ...
    """
    PySide.QtXmlPatterns.QXmlQuery.Qu...
    """

    XmlSchema11IdentityConstraintSelector: ...
    """
    PySide.QtXmlPatterns.QXmlQuery...
    """

    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    def __copy__(self, *args, **kwargs):
        """
        """
        ...

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def bindVariable(self, *args, **kwargs):
        """
        """
        ...

    def evaluateTo(self, *args, **kwargs):
        """
        """
        ...

    def initialTemplateName(self, *args, **kwargs):
        """
        """
        ...

    def isValid(self, *args, **kwargs):
        """
        """
        ...

    def messageHandler(self, *args, **kwargs):
        """
        """
        ...

    def namePool(self, *args, **kwargs):
        """
        """
        ...

    def queryLanguage(self, *args, **kwargs):
        """
        """
        ...

    def setFocus(self, *args, **kwargs):
        """
        """
        ...

    def setInitialTemplateName(self, *args, **kwargs):
        """
        """
        ...

    def setMessageHandler(self, *args, **kwargs):
        """
        """
        ...

    def setQuery(self, *args, **kwargs):
        """
        """
        ...

    def setUriResolver(self, *args, **kwargs):
        """
        """
        ...

    def uriResolver(self, *args, **kwargs):
        """
        """
        ...

    ...

class QXmlResultItems(Shiboken.Object):
    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def current(self, *args, **kwargs):
        """
        """
        ...

    def hasError(self, *args, **kwargs):
        """
        """
        ...

    def next(self, *args, **kwargs):
        """
        """
        ...

    ...

class QXmlSchema(Shiboken.Object):
    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def documentUri(self, *args, **kwargs):
        """
        """
        ...

    def isValid(self, *args, **kwargs):
        """
        """
        ...

    def load(self, *args, **kwargs):
        """
        """
        ...

    def messageHandler(self, *args, **kwargs):
        """
        """
        ...

    def namePool(self, *args, **kwargs):
        """
        """
        ...

    def setMessageHandler(self, *args, **kwargs):
        """
        """
        ...

    def setUriResolver(self, *args, **kwargs):
        """
        """
        ...

    def uriResolver(self, *args, **kwargs):
        """
        """
        ...

    ...

class QXmlSchemaValidator(Shiboken.Object):
    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def messageHandler(self, *args, **kwargs):
        """
        """
        ...

    def namePool(self, *args, **kwargs):
        """
        """
        ...

    def schema(self, *args, **kwargs):
        """
        """
        ...

    def setMessageHandler(self, *args, **kwargs):
        """
        """
        ...

    def setSchema(self, *args, **kwargs):
        """
        """
        ...

    def setUriResolver(self, *args, **kwargs):
        """
        """
        ...

    def uriResolver(self, *args, **kwargs):
        """
        """
        ...

    def validate(self, *args, **kwargs):
        """
        """
        ...

    ...

class QXmlSerializer(QAbstractXmlReceiver):
    __new__: ...
    """
    T.__new__(S, ...) -> a new object with type S, a subtype of T
    """

    def __init__(self, *args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        ...

    def atomicValue(self, *args, **kwargs):
        """
        """
        ...

    def attribute(self, *args, **kwargs):
        """
        """
        ...

    def characters(self, *args, **kwargs):
        """
        """
        ...

    def codec(self, *args, **kwargs):
        """
        """
        ...

    def comment(self, *args, **kwargs):
        """
        """
        ...

    def endDocument(self, *args, **kwargs):
        """
        """
        ...

    def endElement(self, *args, **kwargs):
        """
        """
        ...

    def endOfSequence(self, *args, **kwargs):
        """
        """
        ...

    def namespaceBinding(self, *args, **kwargs):
        """
        """
        ...

    def outputDevice(self, *args, **kwargs):
        """
        """
        ...

    def processingInstruction(self, *args, **kwargs):
        """
        """
        ...

    def setCodec(self, *args, **kwargs):
        """
        """
        ...

    def startDocument(self, *args, **kwargs):
        """
        """
        ...

    def startElement(self, *args, **kwargs):
        """
        """
        ...

    def startOfSequence(self, *args, **kwargs):
        """
        """
        ...

    ...

__all__: ...
"""
['QAbstractMessageHandler', 'QAbstractUriResolver', 'QAbstra...
"""

