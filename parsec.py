from pymonad.Monad import Monad
from pymonad.Monoid import Monoid
from typing import Any, Callable, List, Tuple

Tokens = List[str]
ParserRes = List[Tuple[Any, Tokens]]
ParserFun = Callable[[Tokens], ParserRes]

class Parser(Monad, Monoid):
    def __init__(self, parsec: ParserFun):
        self.parsec = parsec

    def __call__(self, s: Tokens) -> ParserRes:
        return self.parsec(s)

    def fmap(self, f: Callable[[Any], Any]) -> 'Parser':
        def foo(x: str) -> ParserRes:
            res = self.parsec(x)
            return [(f(item[0]), item[1]) for item in res] if res else []
        return Parser(foo)

    @staticmethod
    def unit(c) -> 'Parser':
        return Parser(lambda x: [(c, x)])

    def amap(self, f):
        raise NotImplementedError()

    def bind(self, f: Callable[[Any], 'Parser']) -> 'Parser':
        def _bind(x):
            return sum([f(item[0])(item[1]) for item in self.parsec(x)], [])
        return Parser(_bind)
    
    def __ge__(self, other):
        return self >> (lambda _: other)

    @staticmethod
    def mzero():
        return Parser(lambda x: [])

    def mplus(self, other):
        return Parser(lambda x: self.parsec(x) + other(x))
    
@Parser
def item(x):
    return [(x[0], x[1:])] if x else []

def sat(predict):
    @Parser
    def call(x):
        return Parser.unit(x) if predict(x) else Parser.mzero()
    return item >> call

def word(kw):
    return sat(lambda x: x == kw)

def zerone(p):
    return (p >> (lambda x: Parser.unit(x))) + Parser.mzero()

def many(p):
    return \
        (p      >> (lambda x:
        many(p) >> (lambda xs:
        Parser.unit([x] + xs)))) + Parser.unit([])

def many1(p):
    return p >> (lambda x:
        many(p) >> (lambda xs:
        Parser.unit([x] + xs)))

def sepby1(p, sep):
    return p >> (lambda x:
        many(sep >= p >> (lambda y: Parser.unit(y))) >> (lambda xs:
        Parser.unit([x] + xs)))

def sepby(p, sep):
    return sepby1(p, sep) + Parser.unit([])

def bracket(begin, p, end):
    return begin >= p >> (lambda x: end >= Parser.unit(x))
