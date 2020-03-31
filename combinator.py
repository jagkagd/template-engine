from parsec import *
from node import *
import re

kws = ['for', 'if', 'and', 'or', 'not', 'endif', 'endfor', 'elif', 'else']

name = sat(lambda x: (x not in kws) and re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", x),
           '{} is not a valid variable name.')

@Parser
def tree(s):
    return (many1(node) >> (lambda xs: Parser.unit(Tree(xs))))(s)

@Parser
def node(s):
    return (raw + pipeline + comment + stmt)(s)


comment = bracket(word('{#'), item, word('#}')) \
          >> (lambda x: Parser.unit(Comment(x)))

raw = sat(lambda x: x[0] != r'{', r'{} is started with "{{" in raw.') \
      >> (lambda x: Parser.unit(Raw(repr(x))))

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
    expression     >> (lambda x:
    zerone(params) >> (lambda params:
    Parser.unit(EFilter(x, sum(params, [])))))

pipeline = \
    word('{{')    >= \
    expression    >> (lambda x:
    many(efilter) >> (lambda xs:
    word('}}')    >=
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
    word('or') >= \
    bools      >> (lambda a:
    bools      >> (lambda b:
    Parser.unit(BOr(a, b))))

bnot = \
    word('not') >= \
    bools       >> (lambda a:
    Parser.unit(BNot(a)))

cbranches = \
    bools      >> (lambda predict:
    word('%}') >=
    tree       >> (lambda context:
    Parser.unit((predict, context))))

celse = words('{% else %}') >> node

cif = \
    words('{% if')                     >= \
    sepby(cbranches, words('{% elif')) >> (lambda branches:
    zerone(celse)                      >> (lambda default:
    words('{% endif %}')               >=
    Parser.unit(CIf(branches, default))))

cfor = \
    words('{% for')         >= \
    sepby1(evar, word(',')) >> (lambda xs:
    word('in')              >=
    expression              >> (lambda y:
    word('%}')              >=
    tree                    >> (lambda c:
    words('{% endfor %}') >=
    Parser.unit(CFor(xs, y, c)))))
    
stmt = cfor + cif

# ['<h1> Hello ', '{{', 'name', '|', 'a', '.', 'upper', '|', 'bb', ':', '"', '3', ',', '0', '"', '}}', '!</h1>\n            ', '{%', 'for', 'topic', 'in', 'topics', '%}', '\n                ', '{%', 'if', 'not', 'topic', '%}', '\n                    <p>You are interested in ', '{{', 'topic', '}}', '.</p>\n                ', '{%', 'endif', '%}', '\n            {% endfor }\n            ', '{#', 'aaa', '#}', '\n            ']
# print(tree(['{%', 'for', 'topic', 'in', 'topics', '%}', '\n                ', '{%', 'if', 'not', 'topic', '%}', '\n                    <p>You are interested in ', '{{', 'topic', '}}', '.</p>\n                ', '{%', 'endif', '%}', '\n            ', '{%',  'endfor',  '}', '\n            ']))
