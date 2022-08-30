from collections import deque
from typing import Optional


class Stack:
    data_structure: deque
    size: int

    def __init__(self):
        self.data_structure = deque()
        self.size = 0

    def push(self, element: str) -> None:
        self.data_structure.append(element)
        self.size += 1

    def is_empty(self) -> int:
        return self.size == 0

    def pop(self) -> Optional[str]:
        if self.size == 0:
            return None
        self.size -= 1
        return self.data_structure.pop()