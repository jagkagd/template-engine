from collections import deque


class Contexter:
    def __init__(self):
        self.bounds = deque()
        self.frees = set()

    def block(self, items):
        self.bounds.append([item.repr() for item in items])
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bounds.pop()

    def addFree(self, item):
        if not any([item.repr() in bounds for bounds in self.bounds]):
            self.frees.add(item.repr())
            item.setFree()
        return self

    def __add__(self, other):
        return self.addFree(other)

    def __lshift__(self, other):
        return other.context(self)
