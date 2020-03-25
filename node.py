from dataclasses import dataclass
from typing import List, Tuple, Union
from functools import reduce

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
        writer += self.raw
        return writer

@dataclass
class Pipeline(Node):
    expr: 'Expression'
    filters: List['EFilter']
    def compile(self, writer):
        writer += reduce(
            lambda arg, fun: '{}({})'.format(fun, arg),
            self.filters, self.expr
            )
        return writer
    def context(self, contexter):
        contexter += self.expr
        for filter in self.filters:
            contexter << filter
        return contexter

@dataclass
class Bools:
    def visit(self, visitor):
        visitor << self.left
        visitor << self.right
        return visitor
    def compile(self, writer):
        return self.visit(writer)
    def context(self, contexter):
        return self.visit(contexter)

@dataclass
class BAnd(Bools):
    left: Bools
    right: Bools

@dataclass
class BOr(Bools):
    left: Bools
    right: Bools

@dataclass
class BNot(Bools):
    expr: Bools
    def visit(self, visitor):
        visitor << self.expr
        return visitor

@dataclass
class Expression(Bools):
    def compile(self, writer):
        writer += self
        return writer
    def context(self, contexter):
        contexter += self.var
        return contexter

@dataclass
class EVar(Expression):
    var: str
    free: bool = False
    def __repr__(self):
        return ('c_{}' if self.free else '{}').format(self.var)
    def context(self, contexter):
        contexter += self
        return contexter
    def setFree(self):
        self.free = True

@dataclass
class EDict(Expression):
    var: EVar
    attr: Union[str, int]
    def __repr__(self):
        return '{}.{}'.format(self.var, self.attr)

@dataclass
class EFilter(Expression):
    var: Expression
    args: List[List[str]]
    def context(self, contexter):
        contexter << self.var
        return contexter
    def __repr__(self, arg0=''):
        return '{}({}, {})'.format(
            self.var, arg0, ', '.join(sum(self.args, []))
        )

@dataclass
class Stmt(Node):
    pass

@dataclass
class CIf(Stmt):
    branches: List[Tuple[Bools, Tree]]
    default: Tree
    def compile(self, writer, context):
        for c, (predict, node) in enumerate(self.branches):
            writer += '{} {}:'.format({0: 'if'}.get(c, 'elif'), predict)
            with writer.indent():
                writer << node
        if self.default:
            writer += 'else:'
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
        writer += 'for {item} in {items}:'.format(', '.join(self.item), self.items)
        with writer.indent():
            writer << self.body
        return writer
    def context(self, contexter):
        contexter += self.items
        with contexter.block(self.item):
            contexter << self.body
        return contexter
