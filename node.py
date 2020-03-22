from dataclasses import dataclass
from typing import Any, Callable, List, Tuple, Union
from functools import reduce

@dataclass
class Tree():
    nodes: List['Node']
    def compile(self, writer, context):
        for item in self.seq:
            writer << item
        return writer
    def visit(self, context):
        for item in self.seq:
            item.visit(context)
        return context

@dataclass
class Node:
    pass

@dataclass
class Raw(Node):
    raw: str
    def compile(self, writer):
        return writer << self.raw

@dataclass
class Pipeline(Node):
    expr: 'Expression'
    filters: List['EFilter']
    def compile(self, writer):
        return writer + reduce(
            lambda arg, fun: '{fun}({arg})'.format({'arg': arg.compile(), 'fun': fun.compile()}), 
            self.filters, self.text
            )

@dataclass
class Bools:
    pass

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

@dataclass
class Expression(Bools):
    pass

@dataclass
class EVar(Expression):
    var: str
    def compile(self, writer):
        return writer + '{}'.format(self.var)

@dataclass
class EDict(Expression):
    var: EVar
    attr: Union[str, int]
    def compile(self, writer):
        return writer + '{var}.{attr}'.format(self.var.compile(), self.attr)

@dataclass
class EFilter(Expression):
    func: EVar
    args: Union[str, int]
    def compile(self, writer, arg0):
        return writer + '{func}({arg0}, {args})'.format(
            self.func.compile(), arg0.compile(), 
            ', '.join([arg.compile() for arg in self.args]))

@dataclass
class Stmt(Node):
    pass

@dataclass
class CIf(Stmt):
    branches: List[Tuple[Bools, Tree]]
    default: Tree
    def compile(self, writer, context):
        for c, (predict, node) in enumerate(self.branches):
            writer += '{ifs} {}:'.format({0: 'if'}.get(c, 'elif'), predict)
            with writer.indent():
                writer << node
        if self.default:
            writer += 'else:'
            with writer.indent():
                writer << self.default
        return writer
    def visit(self, context):
        for predict, node in self.branches:
            context << predict
            with context.block(predict):
                node.visit(context)
        if self.default:
            writer += 'else:'
            with writer.indent():
                writer << self.default
        return writer

@dataclass
class CFor(Stmt):
    item: List[EVar]
    items: EVar
    context: Tree
    def compile(self, writer):
        writer << 'for {item} in {items}:'.format(', '.join(self.item), self.items)
        with writer.indent():
            writer << self.context
        return writer
