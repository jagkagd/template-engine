from pymonad.Monad import Monad
from pymonad.Monoid import Monoid
from pymonad.Either import Either, Result, Error
#from pymonad.List import List as mList
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
        return other

'''
class newList(mList):
    @staticmethod
    def mzero(err):
        """ Returns the identity element (an empty List) of the List monoid.  """
        return newList()
'''


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
            return self.parsec(x) >> (lambda a: f(a[0])(a[1]))
        return Parser(_bind)

    def mplus(self, other):
        return Parser(lambda x: self.parsec(x) + other(x))


@Parser
def item(x):
    return Parser.m.unit((x[0], x[1:])) if x else Parser.m.mzero('empty input.')


def sat(predict, msg=r'{} is not satisfied.'):
    @Parser
    def call(x):
        return Parser.unit(x) if predict(x) else Parser.mzero(msg.format(x))
    return item >> call


def word(kw):
    @Parser
    def call(x):
        return Parser.unit(x) if x == kw else Parser.mzero('expect {} but got {}.'.format(kw, x))
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
