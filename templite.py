from combinator import tree
from writer import CodeBuilder
from contexter import Contexter
import re

class TempliteSyntaxError(ValueError):
    pass

class Templite:
    def __init__(self, template, *contexts):
        self.template = template
        self.tokens = self.genTokens(template)
        self.context = {}
        for context in contexts:
            self.context.update(context)
        self.ast, self.remainder = tree((0, self.tokens)).getValue()
        if self.remainder[1]:
            self.templateError(tree(self.remainder).getValue())
        self.varNames = self.ast.context(Contexter())
        self.code = self.ast.compile(CodeBuilder(self.varNames))
        self._render_function = self.code.get_globals()['render_function']

    @staticmethod
    def genTokens(template):
        def clearTokens(tokens):
            return list(filter(lambda x: x != '' and x is not None, tokens))

        #tokens = clearTokens(re.split(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", template))
        tokens = clearTokens(re.split(r"(?s)({{|}}|{%|%}|{#|#}|}|{)", template))
        res = sum([[item] if tokens[i] not in ['{%', '{{'] else re.split(r'(\.|:|\||}}|%}|{%|{{|"|,)|\s', item)
                   for (i, item) in enumerate(tokens[1:])], [tokens[0]])
        return clearTokens(res)

    def templateError(self, err):
        pos, msg = err
        raise TempliteSyntaxError('{} at:\n{}'.format(msg, ' '.join(self.tokens[pos-3:pos+3])))

    def render(self, context=None):
        render_context = dict(self.context)
        if context:
            render_context.update(context)
        return self._render_function(render_context, self._do_dots)

    def _do_dots(self, value, *dots, filter=True):
        for dot in dots:
            try:
                value = getattr(value, dot)
            except AttributeError:
                value = value[dot]
            if (not filter) and callable(value):
                value = value()
        return value
