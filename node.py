from dataclasses import dataclass
from typing import List, Tuple, Union


@dataclass
class Tree:
    nodes: List['Node']

    def visit(self, visitor):
        for node in self.nodes:
            visitor << node
        return visitor

    def compile(self, writer):
        return self.visit(writer)

    def context(self, contexter):
        return self.visit(contexter)


@dataclass
class Node:
    def visit(self, visitor):
        return visitor

    def compile(self, writer):
        return self.visit(writer)

    def context(self, contexter):
        return self.visit(contexter)


@dataclass
class Comment(Node):
    comment: str


@dataclass
class Raw(Node):
    raw: str

    def compile(self, writer):
        return writer * self.raw


@dataclass
class Pipeline(Node):
    expr: 'Expression'
    filters: List['EFilter']

    def compile(self, writer):
        code = self.expr.repr()
        for filter in self.filters:
            code = filter.repr(code)
        return writer * code

    def context(self, contexter):
        contexter << self.expr
        for filter in self.filters:
            contexter << filter
        return contexter


@dataclass
class Bools:
    def repr(self):
        return '({} {} {})'.format(self.flag, self.left.repr(), self.right.repr())

    def context(self, contexter):
        contexter << self.left
        contexter << self.right
        return contexter


@dataclass
class BAnd(Bools):
    left: Bools
    right: Bools
    flag: str = 'and'


@dataclass
class BOr(Bools):
    left: Bools
    right: Bools
    flag: str = 'or'


@dataclass
class BNot(Bools):
    expr: Bools

    def repr(self):
        return '(not {})'.format(self.expr.repr())

    def context(self, contexter):
        contexter << self.expr
        return contexter


@dataclass
class Expression(Bools):
    def compile(self, writer):
        return writer + self.repr

    def context(self, contexter):
        return contexter + self.var


@dataclass
class EVar(Expression):
    var: str
    free: bool = False

    def repr(self):
        return ('c_{}' if self.free else '{}').format(self.var)

    def context(self, contexter):
        return contexter + self

    def setFree(self):
        self.free = True


@dataclass
class EDict(Expression):
    var: EVar
    attr: Union[str, int]

    def repr(self):
        return '{}.{}'.format(self.var.repr(), self.attr)


@dataclass
class EFilter(Expression):
    var: Expression
    args: List[str]

    def context(self, contexter):
        contexter << self.var
        return contexter

    def repr(self, arg0=''):
        return '{}({}{})'.format(
            self.var.repr(), arg0, ''.join([', ' + arg for arg in self.args])
        )


@dataclass
class Stmt(Node):
    pass


@dataclass
class CIf(Stmt):
    branches: List[Tuple[Bools, Tree]]
    default: Tree

    def compile(self, writer):
        for c, (predict, node) in enumerate(self.branches):
            writer + '{} {}:'.format({0: 'if'}.get(c, 'elif'), predict.repr())
            with writer.indent():
                writer << node
        if self.default:
            writer + 'else:'
            with writer.indent():
                writer << self.default[0]
        return writer

    def context(self, contexter):
        for predict, node in self.branches:
            contexter << predict
            contexter << node
        if self.default:
            contexter << self.default[0]
        return contexter


@dataclass
class CFor(Stmt):
    item: List[EVar]
    items: EVar
    body: Tree

    def compile(self, writer):
        writer + 'for {} in {}:'.format(
            ', '.join([it.repr() for it in self.item]),
            self.items.repr())
        with writer.indent():
            writer << self.body
        return writer

    def context(self, contexter):
        contexter + self.items
        with contexter.block(self.item):
            contexter << self.body
        return contexter
