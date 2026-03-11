import tkinter as tk
from core.editor_state import EditorState

class InputHandler:
    def __init__(self, root: tk.Tk, state: EditorState, on_change_callback):
        self.root = root
        self.state = state
        self.on_change = on_change_callback
        
        self.root.bind("<Key>", self._on_key)

    def _on_key(self, event: tk.Event):
        # Shift modifier check (bit 0x1)
        shift_held = bool(event.state & 0x1)

        # Navigation
        if event.keysym == "Up":
            self.state.move_cursor(-1, 0, keep_selection=shift_held)
        elif event.keysym == "Down":
            self.state.move_cursor(1, 0, keep_selection=shift_held)
        elif event.keysym == "Left":
            self.state.move_cursor(0, -1, keep_selection=shift_held)
        elif event.keysym == "Right":
            self.state.move_cursor(0, 1, keep_selection=shift_held)
        elif event.keysym == "Home":
            self.state.move_to_line_start(keep_selection=shift_held)
        elif event.keysym == "End":
            self.state.move_to_line_end(keep_selection=shift_held)
        
        # Typing (Basic)
        elif len(event.char) == 1 and event.char.isprintable():
            if not self.state.selection.is_empty:
                self.state.set_cursor(self.state.document.delete_range(self.state.selection.start, self.state.selection.end))
            new_pos = self.state.document.insert_text(self.state.cursor_pos, event.char)
            self.state.set_cursor(new_pos)
        
        elif event.keysym == "BackSpace":
            if not self.state.selection.is_empty:
                new_pos = self.state.document.delete_range(self.state.selection.start, self.state.selection.end)
                self.state.set_cursor(new_pos)
            elif self.state.cursor_pos.col > 0:
                from core.types import Position
                start = Position(self.state.cursor_pos.line, self.state.cursor_pos.col - 1)
                new_pos = self.state.document.delete_range(start, self.state.cursor_pos)
                self.state.set_cursor(new_pos)
            elif self.state.cursor_pos.line > 0:
                # Merge with previous line
                from core.types import Position
                prev_line_idx = self.state.cursor_pos.line - 1
                prev_line_len = len(self.state.document.get_line(prev_line_idx))
                start = Position(prev_line_idx, prev_line_len)
                new_pos = self.state.document.delete_range(start, self.state.cursor_pos)
                self.state.set_cursor(new_pos)

        elif event.keysym == "Return":
            if not self.state.selection.is_empty:
                self.state.set_cursor(self.state.document.delete_range(self.state.selection.start, self.state.selection.end))
            new_pos = self.state.document.insert_text(self.state.cursor_pos, "\n")
            self.state.set_cursor(new_pos)

        elif event.keysym == "Delete":
            if not self.state.selection.is_empty:
                new_pos = self.state.document.delete_range(self.state.selection.start, self.state.selection.end)
                self.state.set_cursor(new_pos)
            else:
                line_len = len(self.state.document.get_line(self.state.cursor_pos.line))
                if self.state.cursor_pos.col < line_len:
                    from core.types import Position
                    end = Position(self.state.cursor_pos.line, self.state.cursor_pos.col + 1)
                    self.state.document.delete_range(self.state.cursor_pos, end)
                elif self.state.cursor_pos.line < self.state.document.line_count - 1:
                    from core.types import Position
                    end = Position(self.state.cursor_pos.line + 1, 0)
                    self.state.document.delete_range(self.state.cursor_pos, end)

        # Clipboard
        ctrl_held = bool(event.state & 0x4)
        if ctrl_held:
            if event.keysym == "c":
                if not self.state.selection.is_empty:
                    text = self.state.document.get_text_range(self.state.selection.start, self.state.selection.end)
                    self.root.clipboard_clear()
                    self.root.clipboard_append(text)
            elif event.keysym == "x":
                if not self.state.selection.is_empty:
                    text = self.state.document.get_text_range(self.state.selection.start, self.state.selection.end)
                    self.root.clipboard_clear()
                    self.root.clipboard_append(text)
                    new_pos = self.state.document.delete_range(self.state.selection.start, self.state.selection.end)
                    self.state.set_cursor(new_pos)
            elif event.keysym == "v":
                try:
                    text = self.root.clipboard_get()
                    if not self.state.selection.is_empty:
                        self.state.document.delete_range(self.state.selection.start, self.state.selection.end)
                        self.state.set_cursor(self.state.selection.start)
                    new_pos = self.state.document.insert_text(self.state.cursor_pos, text)
                    self.state.set_cursor(new_pos)
                except tk.TclError:
                    pass # Clipboard empty or not text

        self.on_change()
        return "break"
