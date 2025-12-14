import tkinter as tk
from tkinter import font

class CustomEditor(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        # --- canvas ---
        self.canvas = tk.Canvas(self, width=600, height=200, bg="white")
        self.canvas.pack()
        
        # --- font & metrics ---
        self.editor_font = font.Font(family="Courier New", size=16)
        self.char_width = self.editor_font.measure("M")
        self.line_height = self.editor_font.metrics("linespace")
        self.ascent = self.editor_font.metrics("ascent")
        self.descent = self.editor_font.metrics("descent")

        # --- document state ---
        self.text = "Hello, custom editor!"
        self.cursor_pos = 5  # position of the cursor in the text
        
        # --- layout constants ---
        self.left_padding = 10
        self.top_padding = 20
        self.baseline_y = self.top_padding + self.ascent - self.descent # baseline position accounting for tkinter anchor
        
        
        # --- bindings ---
        self.bind_all("<Key>", self.on_key)
        
        # initial draw
        self.render()
        
    def render(self):
        self.canvas.delete("all")
        
        # debug baselines
        self.canvas.create_line(
            0, self.baseline_y, 600, self.baseline_y, fill="#dddddd"
        )
        self.canvas.create_line(
            0, self.top_padding + self.line_height,
            600, self.top_padding + self.line_height,
            fill="#dddddd"
        )
        self.canvas.create_line(
            0, self.top_padding + self.ascent,
            600, self.top_padding + self.ascent,
            fill="#dddddd"
        )
        
        # text
        for i, ch in enumerate(self.text):
            x = self.left_padding + i * self.char_width
            y = self.top_padding + self.ascent
            self.canvas.create_text(
                x, y,
                text=ch,
                font=self.editor_font,
                anchor="sw"
            )
            
        # cursor
        cursor_x = self.left_padding + self.cursor_pos * self.char_width
        self.canvas.create_line(
            cursor_x, self.baseline_y - self.ascent,
            cursor_x, self.baseline_y + self.descent,
            fill="black",
        )
    def on_key(self, event):
        if event.keysym in ("Left", "Right", "Up", "Down"):
            if event.keysym == "Left" and self.cursor_pos > 0:
                self.cursor_pos -= 1
            elif event.keysym == "Right" and self.cursor_pos < len(self.text):
                self.cursor_pos += 1
            else:
                return
            self.render()
            return "break"
            
        if event.char.isprintable():
            self.text = (
                self.text[: self.cursor_pos]
                + event.char
                + self.text[self.cursor_pos :]
            )
            self.cursor_pos += 1
            self.render()
            return "break"
        
        if event.keysym == "BackSpace" and self.cursor_pos > 0:
            self.text = (
                self.text[: self.cursor_pos - 1]
                + self.text[self.cursor_pos :]
            )
            self.cursor_pos -= 1
            self.render()
            return "break"  


# --- basic window ---
root = tk.Tk()
editor = CustomEditor(root)
editor.pack()
root.mainloop()
