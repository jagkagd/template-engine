from pymonad.Monad import Monad
from pymonad.Monoid import Monoid
from pymonad.Either import Either, Result, Error
from functools import reduce


class EitherMonoid(Either, Monoid):
    @classmethod
    def mzero(cls, msg=None):
        return Err(msg)

    @classmethod
    def unit(cls, value):
        return Res(value)


class Res(EitherMonoid, Result):
    def mplus(self, other):
        return self


class Err(EitherMonoid, Error):
    def mplus(self, other):
        if isinstance(other, Err):
            p1, _ = self.getValue()
            p2, _ = other.getValue()
            return self if p1 >= p2 else other
        else:
            return other

def MetaParser(m):
    def wrapper(cls):
        cls.m = m

        def unit(cls, c) -> 'Parser':
            return Parser(lambda x: m.unit((c, x)))

        def mzero(cls, err):
            return Parser(lambda x: m.mzero(err))

        cls.unit = classmethod(unit)
        cls.mzero = classmethod(mzero)

        return cls
    return wrapper


@MetaParser(EitherMonoid)
class Parser(Monad, Monoid):
    def __init__(self, parsec: '\s -> m (a, s)'):
        super().__init__(parsec)
        self.parsec = parsec

    def __call__(self, s: 'tokens') -> 'm (a, s)':
        return self.parsec(s)

    def __ge__(self, other):
        return self >> (lambda _: other)

    def bind(self, f: r'\a -> (\s -> m (b, s))') -> r'\s -> m (b, s)':
        def _bind(x):
            def _f(a):
                return f(a[0])(a[1])
            return self.parsec(x) >> _f
        return Parser(_bind)

    def mplus(self, other):
        return Parser(lambda x: self.parsec(x) + other(x))


@Parser
def getPos(x):
    p, s = x
    return Parser.m.unit((p, (p, s)))


@Parser
def item(x):
    p, s = x
    return Parser.m.unit((s[0], (p+1, s[1:]))) if s else \
        Parser.m.mzero((p+1, 'Unfinished template.'))


def sat(predict, msg=r'{} is not satisfied.'):
    @Parser
    def call(x):
        return Parser.unit(x) if predict(x) else \
            getPos >> (lambda p: Parser.mzero((p, msg.format(x))))
    return item >> call


def word(kw):
    @Parser
    def call(x):
        return Parser.unit(x) if x == kw else \
            getPos >> (lambda p: Parser.mzero((p, 'Expected "{}" but got "{}"'.format(kw, x))))
    return item >> call


def words(kws):
    tokens = kws.split(' ')
    return reduce(lambda x, y: x >= y, [word(kw) for kw in tokens])


def zerone(p):
    return (p >> (lambda x: Parser.unit([x]))) + Parser.unit([])


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
