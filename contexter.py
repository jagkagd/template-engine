from collections import deque


class Contexter:
    def __init__(self):
        self.bounds = deque()
        self.frees = set()

    def block(self, items):
        self.bounds.append([str(item) for item in items])
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bounds.pop()

    def addFree(self, item):
        if not any([str(item) in bounds for bounds in self.bounds]):
            self.frees.add(str(item))
            item.setFree()
        return self

    def __iadd__(self, other):
        return self.addFree(other)

    def __lshift__(self, other):
        return other.context(self)
