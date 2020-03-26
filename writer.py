class CodeBuilder:
    def __init__(self, context):
        self.code = []
        self.context = context
        self.indent_level = 0
        self + "def render_function(context, do_dots):"
        self.indent()
        self + "result = []"
        self + "append_result = result.append"
        self + "extend_result = result.extend"
        self + "to_str = str"
        for var in self.context.frees:
            self + "c_{} = context['{}']".format(var, var)

    def add_line(self, line):
        self.code.append((self.indent_level, line))
        return self

    def __add__(self, line):
        return self.add_line(line)

    def __mul__(self, line):
        return self.add_line('append_result({})'.format(line))

    def __lshift__(self, other):
        return other.compile(self)

    def indent(self):
        self.indent_level += 1
        return self

    def dedent(self):
        self.indent_level -= 1
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.indent_level -= 1

    def __repr__(self):
        return '\n'.join(' '*indent*4 + str(c) for (indent, c) in self.code)

    def get_globals(self):
        self + "return ''.join(result)"
        python_source = str(self)
        global_namespace = {}
        exec(python_source, global_namespace)
        return global_namespace
