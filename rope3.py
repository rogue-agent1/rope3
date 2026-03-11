#!/usr/bin/env python3
"""Rope data structure — efficient string editing for text editors.

One file. Zero deps. Does one thing well.

Balanced binary tree of string fragments. O(log n) insert, delete, index.
Used in text editors (Xi, VS Code's PieceTable is similar).
"""
import sys

class RopeNode:
    __slots__ = ('left', 'right', 'text', 'weight', 'height')
    def __init__(self, text=None, left=None, right=None):
        if text is not None:
            self.text = text
            self.left = self.right = None
            self.weight = len(text)
            self.height = 0
        else:
            self.text = None
            self.left = left
            self.right = right
            self.weight = _length(left)
            self.height = 1 + max(_height(left), _height(right))

def _length(node):
    if node is None: return 0
    if node.text is not None: return len(node.text)
    return node.weight + _length(node.right)

def _height(node):
    return node.height if node else -1

def _balance(node):
    return _height(node.left) - _height(node.right) if node and node.text is None else 0

def _rotate_right(y):
    x = y.left
    y.left = x.right
    x.right = RopeNode(left=y.left, right=y.right) if y.text is None else y
    # Rebuild y
    if y.text is None:
        y_new = RopeNode(left=y.left, right=y.right)
    else:
        y_new = y
    x_new = RopeNode(left=x.left, right=y_new)
    return x_new

def _rotate_left(x):
    y = x.right
    x.right = y.left
    x_new = RopeNode(left=x.left, right=x.right) if x.text is None else x
    if x.text is None:
        x_new = RopeNode(left=x.left, right=x.right)
    else:
        x_new = x
    y_new = RopeNode(left=x_new, right=y.right)
    return y_new

class Rope:
    LEAF_MAX = 64

    def __init__(self, text=""):
        self.root = self._build(text) if text else None

    def _build(self, text):
        if len(text) <= self.LEAF_MAX:
            return RopeNode(text=text)
        mid = len(text) // 2
        return RopeNode(left=self._build(text[:mid]), right=self._build(text[mid:]))

    def __len__(self):
        return _length(self.root)

    def __str__(self):
        parts = []
        self._collect(self.root, parts)
        return "".join(parts)

    def _collect(self, node, parts):
        if node is None: return
        if node.text is not None:
            parts.append(node.text)
        else:
            self._collect(node.left, parts)
            self._collect(node.right, parts)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return str(self)[idx]
        if idx < 0: idx += len(self)
        return self._index(self.root, idx)

    def _index(self, node, idx):
        if node.text is not None:
            return node.text[idx]
        if idx < node.weight:
            return self._index(node.left, idx)
        return self._index(node.right, idx - node.weight)

    def insert(self, pos, text):
        new_node = self._build(text)
        if self.root is None:
            self.root = new_node
            return
        left, right = self._split(self.root, pos)
        self.root = RopeNode(left=RopeNode(left=left, right=new_node), right=right)

    def delete(self, start, length):
        left, rest = self._split(self.root, start)
        _, right = self._split(rest, length)
        self.root = RopeNode(left=left, right=right) if left and right else (left or right)

    def _split(self, node, pos):
        if node is None: return None, None
        if node.text is not None:
            if pos <= 0: return None, node
            if pos >= len(node.text): return node, None
            return RopeNode(text=node.text[:pos]), RopeNode(text=node.text[pos:])
        if pos <= node.weight:
            left, right = self._split(node.left, pos)
            return left, RopeNode(left=right, right=node.right)
        else:
            left, right = self._split(node.right, pos - node.weight)
            return RopeNode(left=node.left, right=left), right

    def substring(self, start, end):
        return str(self)[start:end]


def main():
    r = Rope("Hello, World!")
    print(f"Initial:  '{r}' (len={len(r)})")
    r.insert(7, "Beautiful ")
    print(f"Insert:   '{r}'")
    r.delete(7, 10)
    print(f"Delete:   '{r}'")
    r.insert(5, " Cruel")
    print(f"Insert:   '{r}'")
    print(f"Char[0]:  '{r[0]}'")
    print(f"Char[-1]: '{r[-1]}'")
    print(f"Slice:    '{r[0:5]}'")
    # Stress test
    import time
    big = Rope("x" * 100000)
    t0 = time.perf_counter()
    for i in range(1000):
        big.insert(len(big) // 2, "y")
    dt = time.perf_counter() - t0
    print(f"\n1000 mid-insertions on 100K rope: {dt*1000:.1f}ms (len={len(big)})")

if __name__ == "__main__":
    main()
