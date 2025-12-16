import tkinter as tk
from tkinter import font

# TODO: implement single index for cursor position instead of (x, y)

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
        self.text = "Hello World\nThis is a sample text\nEach line is separated by a newline character\nPython handles this using \\n"
        self.cursor_pos_x = 5  # position of the cursor in the text
        self.cursor_pos_y = 0
        
        # --- layout constants ---
        self.left_padding = 10
        self.top_padding = 20
        self.baseline_y = self.top_padding + self.ascent - self.descent # baseline position accounting for tkinter anchor
        # self.max_lines = 1  # first line
        
        # --- bindings ---
        self.bind_all("<Key>", self.on_key)
        
        # initial draw
        self.render()
        
    def draw_debug_baselines(self):
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
        
    def render(self):
        self.canvas.delete("all")
        max_y = self.top_padding + self.ascent
        # debug baselines
        # self.canvas.create_line(
        #     0, self.baseline_y, 600, self.baseline_y, fill="#dddddd"
        # )
        # self.canvas.create_line(
        #     0, self.top_padding + self.line_height,
        #     600, self.top_padding + self.line_height,
        #     fill="#dddddd"
        # )
        # self.canvas.create_line(
        #     0, self.top_padding + self.ascent,
        #     600, self.top_padding + self.ascent,
        #     fill="#dddddd"
        # )
        
        # text
        x = self.left_padding
        y = self.top_padding + self.ascent
        for i, ch in enumerate(self.text):
            if ch == "\n":
                y += self.line_height
                x = self.left_padding
                continue
            else:
                self.canvas.create_text(
                    x, y,
                    text=ch,
                    font=self.editor_font,
                    anchor="sw"
                )
                x += self.char_width
        
        # cursor
        cursor_x = self.left_padding + self.cursor_pos_x * self.char_width
        cursor_y = self.top_padding - self.descent + self.cursor_pos_y * self.line_height
        self.canvas.create_line(
            cursor_x, cursor_y,
            cursor_x, cursor_y + self.ascent + self.descent,
            fill="black",
        )
    def on_key(self, event):
        if event.keysym in ("Left", "Right", "Up", "Down"):
            if event.keysym == "Left" and self.cursor_pos_x > 0:
                self.cursor_pos_x -= 1
            elif event.keysym == "Right" and self.cursor_pos_x < len(self.text):
                self.cursor_pos_x += 1
            elif event.keysym == "Up":
                self.cursor_pos_y -= 1
            elif event.keysym == "Down":
                self.cursor_pos_y += 1
            else:
                return
            self.render()
            return "break"
            
        if event.char.isprintable():
            self.text = (
                self.text[: self.cursor_pos_x]
                + event.char
                + self.text[self.cursor_pos_x :]
            )
            self.cursor_pos_x += 1
            self.render()
            return "break"
        
        if event.keysym == "BackSpace" and self.cursor_pos_x > 0:
            self.text = (
                self.text[: self.cursor_pos_x - 1]
                + self.text[self.cursor_pos_x :]
            )
            self.cursor_pos_x -= 1
            self.render()
            return "break"  


# --- basic window ---
root = tk.Tk()
editor = CustomEditor(root)
editor.pack()
root.mainloop()
