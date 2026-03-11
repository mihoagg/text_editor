from tkinter import font
from core.types import Position

class LayoutManager:
    def __init__(self, canvas, font_family="Courier New", font_size=16):
        self.canvas = canvas
        self.editor_font = font.Font(family=font_family, size=font_size)
        self.char_width = self.editor_font.measure("M")
        self.line_height = self.editor_font.metrics("linespace")
        self.left_padding = 10

    def get_pixel_coords(self, pos: Position, scroll_y: int) -> tuple[int, int]:
        x = self.left_padding + pos.col * self.char_width
        y = pos.line * self.line_height - scroll_y
        return x, y

    def get_position_at_pixels(self, x: int, y: int, scroll_y: int, line_count: int, lines: list[str]) -> Position:
        doc_y = y + scroll_y
        line_idx = doc_y // self.line_height
        line_idx = max(0, min(line_idx, line_count - 1))
        
        col_idx = (x - self.left_padding) // self.char_width
        line_len = len(lines[line_idx])
        col_idx = max(0, min(col_idx, line_len))
        
        # Check if cursor is past half a character
        char_start_x = self.left_padding + col_idx * self.char_width
        if x - char_start_x > self.char_width / 2:
            col_idx = min(col_idx + 1, line_len)
            
        return Position(line_idx, col_idx)
