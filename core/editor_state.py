from dataclasses import dataclass
from .types import Position, SelectionRange
from .document import Document

class EditorState:
    def __init__(self, document: Document):
        self.document = document
        self.cursor_pos = Position(0, 0)
        self.selection = SelectionRange(self.cursor_pos, self.cursor_pos)
        self.scroll_y = 0
        self.preferred_col = 0 # To handle moving Up/Down across lines of different lengths

    def set_cursor(self, pos: Position, keep_selection: bool = False):
        # Clamp cursor to document bounds
        line = max(0, min(pos.line, self.document.line_count - 1))
        col = max(0, min(pos.col, len(self.document.get_line(line))))
        new_pos = Position(line, col)
        
        self.cursor_pos = new_pos
        if not keep_selection:
            self.selection = SelectionRange(new_pos, new_pos)
        else:
            self.selection = SelectionRange(self.selection.anchor, new_pos)
        
        # Update preferred column when moving horizontally
        if not keep_selection:
            self.preferred_col = col

    def move_cursor(self, d_line: int, d_col: int, keep_selection: bool = False):
        new_line = self.cursor_pos.line + d_line
        
        if d_line != 0:
            # Moving Up/Down: Use preferred column
            new_line = max(0, min(new_line, self.document.line_count - 1))
            new_col = min(self.preferred_col, len(self.document.get_line(new_line)))
            self.set_cursor(Position(new_line, new_col), keep_selection)
        else:
            # Moving Left/Right: Update preferred column
            new_col = self.cursor_pos.col + d_col
            self.set_cursor(Position(new_line, new_col), keep_selection)
            self.preferred_col = self.cursor_pos.col

    def move_to_line_start(self, keep_selection: bool = False):
        self.set_cursor(Position(self.cursor_pos.line, 0), keep_selection)

    def move_to_line_end(self, keep_selection: bool = False):
        line_len = len(self.document.get_line(self.cursor_pos.line))
        self.set_cursor(Position(self.cursor_pos.line, line_len), keep_selection)
