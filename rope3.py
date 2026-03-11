#!/usr/bin/env python3
"""Rope — efficient string data structure for text editors."""
import sys

class RopeNode:
    __slots__ = ('left', 'right', 'text', 'weight')
    def __init__(self, text=None, left=None, right=None):
        if text is not None:
            self.text, self.left, self.right = text, None, None
            self.weight = len(text)
        else:
            self.text, self.left, self.right = None, left, right
            self.weight = self._len(left)
    @staticmethod
    def _len(node):
        if node is None: return 0
        if node.text is not None: return len(node.text)
        return node.weight + RopeNode._len(node.right)

class Rope:
    LEAF_MAX = 64
    def __init__(self, text=""):
        self.root = self._build(text) if text else None
    def _build(self, text):
        if len(text) <= self.LEAF_MAX: return RopeNode(text)
        mid = len(text) // 2
        return RopeNode(left=self._build(text[:mid]), right=self._build(text[mid:]))
    def __len__(self): return RopeNode._len(self.root) if self.root else 0
    def __getitem__(self, idx):
        if isinstance(idx, slice):
            start, stop, _ = idx.indices(len(self))
            return ''.join(self._index(self.root, i) for i in range(start, stop))
        if idx < 0: idx += len(self)
        return self._index(self.root, idx)
    def _index(self, node, idx):
        if node.text is not None: return node.text[idx]
        if idx < node.weight: return self._index(node.left, idx)
        return self._index(node.right, idx - node.weight)
    def insert(self, idx, text):
        left, right = self._split(self.root, idx)
        mid = self._build(text)
        self.root = RopeNode(left=RopeNode(left=left, right=mid), right=right)
    def delete(self, start, length):
        left, rest = self._split(self.root, start)
        _, right = self._split(rest, length)
        self.root = RopeNode(left=left, right=right) if left and right else (left or right)
    def _split(self, node, idx):
        if node is None: return None, None
        if node.text is not None:
            return (RopeNode(node.text[:idx]), RopeNode(node.text[idx:])) if 0 < idx < len(node.text) else (node, None) if idx >= len(node.text) else (None, node)
        if idx <= node.weight:
            ll, lr = self._split(node.left, idx)
            return ll, RopeNode(left=lr, right=node.right)
        else:
            rl, rr = self._split(node.right, idx - node.weight)
            return RopeNode(left=node.left, right=rl), rr
    def __str__(self):
        parts = []; self._collect(self.root, parts); return ''.join(parts)
    def _collect(self, node, parts):
        if node is None: return
        if node.text is not None: parts.append(node.text); return
        self._collect(node.left, parts); self._collect(node.right, parts)

if __name__ == "__main__":
    r = Rope("Hello, World!")
    print(f"Initial: {r} (len={len(r)})")
    r.insert(7, "Beautiful ")
    print(f"After insert: {r}")
    r.delete(7, 10)
    print(f"After delete: {r}")
    print(f"Slice [0:5]: {r[0:5]}")
