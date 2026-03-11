from dataclasses import dataclass

@dataclass(frozen=True)
class Position:
    line: int
    col: int

@dataclass(frozen=True)
class SelectionRange:
    anchor: Position
    active: Position

    @property
    def start(self) -> Position:
        if self.anchor.line < self.active.line:
            return self.anchor
        if self.anchor.line > self.active.line:
            return self.active
        return self.anchor if self.anchor.col < self.active.col else self.active

    @property
    def end(self) -> Position:
        if self.anchor.line < self.active.line:
            return self.active
        if self.anchor.line > self.active.line:
            return self.anchor
        return self.active if self.anchor.col < self.active.col else self.anchor

    @property
    def is_empty(self) -> bool:
        return self.anchor == self.active
