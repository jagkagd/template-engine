class CodeBuilder:
    def __init__(self, code=[]):
        self.code = code
        self.indent_level = 0

    def add_line(self, line):
        self.code.append((self.indent_level, line))

    def __iadd__(self, line):
        self.add_line(line)

    def __lshift__(self, other):
        return other.compile(self)

    def indent(self):
        self.indent_level += 1

    def __enter__(self):
        return self

    def __exit__(self):
        self.indent_level -= 1

    def __repr__(self):
        return '\n'.join(' '*indent*4 + str(c) for (indent, c) in self.code)

    def get_globals(self):
        self.code.insert((0, "def render_function(context, do_dots):"))
        self.code.insert((1, "result = []"))
        self.code.insert((1, "append_result = result.append"))
        self.code.insert((1, "extend_result = result.extend"))
        self.code.insert((1, "to_str = str"))
        self += "return ''.join(result)"

        python_source = str(self)
        global_namespace = {}
        exec(python_source, global_namespace)
        return global_namespace

