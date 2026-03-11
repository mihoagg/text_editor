from typing import List
from .types import Position

class Document:
    def __init__(self, initial_text: str = ""):
        self._lines: List[str] = initial_text.splitlines()
        if not self._lines:
            self._lines = [""]
        if initial_text.endswith('\n'):
            self._lines.append("")

    @property
    def lines(self) -> List[str]:
        return self._lines

    @property
    def line_count(self) -> int:
        return len(self._lines)

    def get_line(self, line_index: int) -> str:
        if 0 <= line_index < self.line_count:
            return self._lines[line_index]
        return ""

    def insert_text(self, pos: Position, text: str) -> Position:
        """Inserts text at the given position and returns the new position."""
        lines_to_insert = text.split('\n')
        if not lines_to_insert:
            return pos

        current_line = self._lines[pos.line]
        before = current_line[:pos.col]
        after = current_line[pos.col:]

        if len(lines_to_insert) == 1:
            self._lines[pos.line] = before + lines_to_insert[0] + after
            return Position(pos.line, pos.col + len(lines_to_insert[0]))
        
        # Multiline insert
        first_line_part = before + lines_to_insert[0]
        last_line_part = lines_to_insert[-1] + after
        
        mid_lines = lines_to_insert[1:-1]
        
        new_lines = [first_line_part] + mid_lines + [last_line_part]
        
        self._lines[pos.line : pos.line + 1] = new_lines
        
        return Position(pos.line + len(lines_to_insert) - 1, len(lines_to_insert[-1]))

    def delete_range(self, start: Position, end: Position) -> Position:
        """Deletes text between start and end and returns the new position."""
        if start == end:
            return start

        if start.line == end.line:
            line = self._lines[start.line]
            self._lines[start.line] = line[:start.col] + line[end.col:]
        else:
            first_line = self._lines[start.line][:start.col]
            last_line = self._lines[end.line][end.col:]
            self._lines[start.line : end.line + 1] = [first_line + last_line]
            
        return start

    def get_text_range(self, start: Position, end: Position) -> str:
        if start == end:
            return ""
        
        if start.line == end.line:
            return self._lines[start.line][start.col : end.col]
        
        result = [self._lines[start.line][start.col :]]
        result.extend(self._lines[start.line + 1 : end.line])
        result.append(self._lines[end.line][: end.col])
        return "\n".join(result)
