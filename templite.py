from combinator import tree
import re


class Templite:
    def __init__(self, template, *contexts, genAST=tree, genCode=None):
        self.template = template
        self.tokens = self.genTokens(template)
        self.context = {}
        for context in contexts:
            self.context.update(context)
        self.genAST = genAST
        self.genCode = genCode
        self.ast = self.genAST(self.tokens)
        self.varNames = genFreeVar(self.ast)

    @staticmethod
    def genTokens(template):
        def clearTokens(tokens):
            return list(filter(lambda x: x != '' and x is not None, tokens))

        tokens = clearTokens(re.split(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", template))
        res = sum([[item] if item[0] != '{' else re.split(r'(\.|:|\||}}|%}|{%|{{|"|,)|\s', item) for item in tokens], [])
        return clearTokens(res)



print(Templite('''<h1> Hello {{name|a.upper|bb:"3, 0"}}!</h1>
            {% for topic in topics %}
                {% if topic %}
                    <p>You are interested in {{topic}}.</p>
                {% endif %}
            {% endfor %}
            {# aaa #}
            ''', {}).ast)