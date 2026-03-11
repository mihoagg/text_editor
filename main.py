import tkinter as tk
from core.document import Document
from core.editor_state import EditorState
from core.types import Position
from ui.layout import LayoutManager
from ui.renderer import Renderer
from ui.input_handler import InputHandler
from ui.scroll import ScrollManager

class EditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("New Text Editor")

        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        doc = Document("Hello World\n" + "\n".join([f"Line {i}" for i in range(1, 51)]))
        self.state = EditorState(doc)

        self.layout = LayoutManager(self.canvas)
        self.renderer = Renderer(self.canvas)
        self.scroll = ScrollManager(self.state, self.layout, self.canvas.winfo_height)
        
        # Phase 2: Input Handling
        self.input = InputHandler(self.root, self.state, self.render)

        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        
        self.render()

    def on_click(self, event):
        pos = self.layout.get_position_at_pixels(
            event.x, event.y, self.state.scroll_y, 
            self.state.document.line_count, self.state.document.lines
        )
        self.state.set_cursor(pos)
        self.render()

    def on_drag(self, event):
        pos = self.layout.get_position_at_pixels(
            event.x, event.y, self.state.scroll_y, 
            self.state.document.line_count, self.state.document.lines
        )
        self.state.set_cursor(pos, keep_selection=True)
        self.render()

    def on_mouse_wheel(self, event):
        # In Windows, delta is usually 120 or -120
        delta = -1 * (event.delta // 120) * (self.layout.line_height * 3)
        self.scroll.scroll_by(delta)
        self.render()

    def on_resize(self, event):
        self.render()

    def render(self):
        # 0. Update Viewport
        self.scroll.ensure_cursor_visible()
        
        self.renderer.clear()
        
        # 1. Mediator logic: Calculate what to show
        height = self.canvas.winfo_height()
        visible_count = (height // self.layout.line_height) + 2
        start_line_idx = self.state.scroll_y // self.layout.line_height
        end_line_idx = min(self.state.document.line_count, start_line_idx + visible_count)

        # 2. Mediator logic: Coordinate Selection
        if not self.state.selection.is_empty:
            sel_start = self.state.selection.start
            sel_end = self.state.selection.end
            for line_idx in range(sel_start.line, sel_end.line + 1):
                line_text = self.state.document.get_line(line_idx)
                col_start = sel_start.col if line_idx == sel_start.line else 0
                col_end = sel_end.col if line_idx == sel_end.line else len(line_text)
                
                x1, y1 = self.layout.get_pixel_coords(Position(line_idx, col_start), self.state.scroll_y)
                x2, _ = self.layout.get_pixel_coords(Position(line_idx, col_end), self.state.scroll_y)
                
                # Visual hint for empty newline selections
                if x1 == x2 and sel_start.line != sel_end.line:
                    x2 += 5
                
                self.renderer.draw_selection_rect(x1, y1, x2, y1 + self.layout.line_height)

        # 3. Mediator logic: Coordinate Text
        for i in range(start_line_idx, end_line_idx):
            line_text = self.state.document.get_line(i)
            x, y = self.layout.get_pixel_coords(Position(i, 0), self.state.scroll_y)
            self.renderer.draw_text_line(x, y, line_text)

        # 4. Mediator logic: Coordinate Cursor
        cx, cy = self.layout.get_pixel_coords(self.state.cursor_pos, self.state.scroll_y)
        self.renderer.draw_cursor(cx, cy, self.layout.line_height)


if __name__ == "__main__":
    root = tk.Tk()
    app = EditorApp(root)
    root.mainloop()
