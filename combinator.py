from parsec import *
from node import *

kws = ['for', 'if', 'and', 'or', 'not', 'endif', 'endfor', 'elif', 'else']

name = sat(lambda x: x not in kws)

@Parser
def tree(s):
    return (many1(node) >> (lambda xs: Parser.unit(Tree(xs))))(s)

@Parser
def node(s):
    return (raw + pipeline + stmt)(s)

raw = sat(lambda x: x[0] == '<') >> (lambda x: Raw(x))

evar = name >> (lambda x: Parser.unit(EVar(x)))

edict = \
    evar      >> (lambda x:
    word('.') >=
    item      >> (lambda a:
    Parser.unit(EDict(x, a))))

expression = edict + evar

params = \
    word(':') >= \
    bracket(word('"'), sepby1(item, word(',')), word('"'))

efilter = \
    word('|')      >= \
    evar           >> (lambda x:
    zerone(params) >> (lambda params:
    Parser.unit(EFilter(x, xs))))

pipeline = \
    expression    >> (lambda x:
    many(efilter) >> (lambda xs:
    Parser.unit(Pipeline(x, xs))))

@Parser
def bools(s):
    return (band + bor + bnot + expression)(s)

band = \
    word('and') >= \
    bools       >> (lambda a:
    bools       >> (lambda b:
    Parser.unit(BAnd(a, b))))

bor = \
    word('or')  >= \
    bools       >> (lambda a:
    bools       >> (lambda b:
    Parser.unit(BOr(a, b))))

bnot = \
    word('not') >= \
    bools       >> (lambda a:
    Parser.unit(BNot(a)))

cbranches = \
    bools >> (lambda predict:
    word(':') >=
    tree >> (lambda context:
    Parser.unit([(predict, context)])))

celse = word('else') >= word(':') >> node

cif = \
    word('if')                     >= \
    sepby(cbranches, word('elif') >= word(':')) >> (lambda branches:
    zerone(celse)                  >> (lambda default:
    word('endif')                  >=
    Parser.unit(CIf(branches, default))))

cfor = \
    word('for')             >= \
    sepby1(evar, word(',')) >> (lambda xs:
    word('in')              >=
    expression              >> (lambda y:
    word(':')               >=
    tree                    >> (lambda c:
    word('endfor')          >=
    Parser.unit(CFor(xs, y, c)))))
    
stmt = cfor + cif

print(celse(['else', ':', 'cc']))
print(node(['aa', '.', 'bb']))