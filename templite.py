from combinator import tree
from writer import CodeBuilder
from contexter import Contexter
import re


class Templite:
    def __init__(self, template, *contexts):
        self.template = template
        self.tokens = self.genTokens(template)
        self.context = {}
        for context in contexts:
            self.context.update(context)
        self.ast = tree(self.tokens).getValue()[0]
        self.varNames = self.ast.context(Contexter())
        self.code = self.ast.compile(CodeBuilder(self.varNames))
        self._render_function = self.code.get_globals()['render_function']

    @staticmethod
    def genTokens(template):
        def clearTokens(tokens):
            return list(filter(lambda x: x != '' and x is not None, tokens))

        tokens = clearTokens(re.split(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", template))
        res = sum([[item] if item[0] != '{' else re.split(r'(\.|:|\||}}|%}|{%|{{|"|,)|\s', item)
                   for item in tokens], [])
        return clearTokens(res)

    def render(self, context=None):
        render_context = dict(self.context)
        if context:
            render_context.update(context)
        return self._render_function(render_context, self._do_dots)

    def _do_dots(self, value, attr):
        try:
            return getattr(value, attr)
        except AttributeError:
            return value[attr]
