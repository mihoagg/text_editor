import tkinter as tk

class Renderer:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.colors = {
            "bg": "white",
            "text": "black",
            "selection": "#CCE8FF",
            "cursor": "black"
        }
        # We'll store font locally just for the create_text call
        self.font = ("Courier New", 16)

    def clear(self):
        self.canvas.delete("all")

    def draw_text_line(self, x: int, y: int, text: str):
        self.canvas.create_text(
            x, y,
            text=text,
            font=self.font,
            anchor="nw",
            fill=self.colors["text"]
        )

    def draw_cursor(self, x: int, y: int, line_height: int):
        self.canvas.create_line(
            x, y,
            x, y + line_height,
            fill=self.colors["cursor"],
            width=2
        )

    def draw_selection_rect(self, x1: int, y1: int, x2: int, y2: int):
        self.canvas.create_rectangle(
            x1, y1,
            x2, y2,
            fill=self.colors["selection"],
            outline=""
        )
