from core.editor_state import EditorState
from ui.layout import LayoutManager

class ScrollManager:
    def __init__(self, state: EditorState, layout: LayoutManager, canvas_height_getter):
        self.state = state
        self.layout = layout
        self.get_canvas_height = canvas_height_getter

    def scroll_by(self, delta: int):
        self.state.scroll_y += delta
        self._clamp_scroll()

    def scroll_to(self, y: int):
        self.state.scroll_y = y
        self._clamp_scroll()

    def ensure_cursor_visible(self):
        # Calculate cursor vertical position relative to viewport
        cursor_y_top = self.state.cursor_pos.line * self.layout.line_height
        cursor_y_bottom = cursor_y_top + self.layout.line_height
        
        viewport_top = self.state.scroll_y
        viewport_bottom = viewport_top + self.get_canvas_height()
        
        # Margin to keep cursor from hitting the very edge
        # margin = self.layout.line_height
        margin = 0
        
        if cursor_y_top < viewport_top + margin:
            # Scroll Up
            self.scroll_to(cursor_y_top - margin)
        elif cursor_y_bottom > viewport_bottom - margin:
            # Scroll Down
            self.scroll_to(cursor_y_bottom - viewport_bottom + viewport_top + margin)

    def _clamp_scroll(self):
        max_scroll = max(0, (self.state.document.line_count * self.layout.line_height) - self.get_canvas_height() + 50)
        self.state.scroll_y = max(0, min(self.state.scroll_y, max_scroll))
