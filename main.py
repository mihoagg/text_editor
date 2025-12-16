import tkinter as tk
from tkinter import font

# TODO: maybe implement single index for cursor position instead of (x, y)
# INPUT LAYER:
# Scrolling and copy paste, undo redo, mouse support
# TEXT LAYOUT LAYER:
# Line wrapping 
# Syntax highlighting, bidi text, complex scripts


# RENDERING LAYER:
# Smooth scrolling, hardware acceleration
# Plugin system for rendering (eg. minimap, line numbers, etc.)


# Document model layer:
# Efficient data structures for text storage and manipulation
# Multiple documents/tabs support
# File I/O operations
# Integration with external tools (e.g., linters, formatters)


# User interface layer:
# Menus, toolbars, status bars
# Customizable themes and settings
# Search and replace functionality
# Collaboration features (real-time editing with others)


# Performance optimizations:
# Lazy rendering, caching mechanisms
# Profiling and benchmarking tools
# Testing framework for editor features

# Accessibility features:
# Keyboard navigation, screen reader support
# High contrast themes, adjustable font sizes
# Internationalization and localization support

# Plugin architecture:
# API for third-party extensions



class CustomEditor(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        # --- canvas ---
        self.canvas = tk.Canvas(self, width=600, height=200, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
        
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
        self.preferred_cursor_x = self.cursor_pos_x  # for vertical movements
        
        # --- layout constants ---
        self.left_padding = 10
        self.top_padding = 20
        self.baseline_y = self.top_padding + self.ascent - self.descent # baseline position accounting for tkinter anchor
        # self.max_lines = 1  # first line
        
        # --- bindings ---
        self.bind_all("<Key>", self.on_key)
                
        # --- initial setup ---
        self.text = self.parse_text()
        self.trailing_line()
        
        # initial draw
        self.render()
        
    def parse_text(self):
        # split text into lines based on newline characters
        lines = self.text.split("\n")
        return lines
    
    def on_canvas_resize(self, event):
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
        
        # text
        y = self.top_padding + self.ascent
        for line in self.text:
            x = self.left_padding
            for ch in line:
                self.canvas.create_text(
                    x, y,
                    text=ch,
                    font=self.editor_font,
                    anchor="sw"
                )
                x += self.char_width
            y += self.line_height
        
        # cursor
        cursor_x = self.left_padding + self.cursor_pos_x * self.char_width
        cursor_y = self.top_padding - self.descent + self.cursor_pos_y * self.line_height
        self.canvas.create_line(
            cursor_x, cursor_y,
            cursor_x, cursor_y + self.ascent + self.descent,
            fill="black",
        )
    def move_cursor(self, direction: str): #TODO handle line joins and splits and go back to previous line on left at x=0
        if direction == "left":
            self.cursor_pos_x -= 1
            self.normalize_cursor_position()
            self.preferred_cursor_x = self.cursor_pos_x
        elif direction == "right":
            self.cursor_pos_x += 1
            self.normalize_cursor_position()
            self.preferred_cursor_x = self.cursor_pos_x
        elif direction == "down":
            self.cursor_pos_y += 1
            self.normalize_cursor_position(use_preferred=True)
        elif direction == "up":
            self.cursor_pos_y -= 1
            self.normalize_cursor_position(use_preferred=True)
        
    def normalize_cursor_position(self, use_preferred: bool = False):
        '''
        check x,y cursor position and adjust if out of bounds
        left: x > 0 , update preferred x
        right: x <= line length , update preferred x
        
        up: y > 0                                  
        down: y < number of lines - 1 (start by 0) 
        
        Preferred column
        Set cursor_x = min(preferred_x, line_length) on vertical movements
        '''
       
        # Vertical bounds
        self.cursor_pos_y = max(self.cursor_pos_y, 0)
        self.cursor_pos_y = min(self.cursor_pos_y, len(self.text) - 1)   
        
        line = self.text[self.cursor_pos_y]
        
        # Horizontal bounds
        if use_preferred:
            self.cursor_pos_x = min(self.preferred_cursor_x, len(line))
        else:
            self.cursor_pos_x = max(self.cursor_pos_x, 0)
            self.cursor_pos_x = min(self.cursor_pos_x, len(line))      
        return
    
    def trailing_line(self):
        if self.text[-1] != "":
            self.text.append("")  # ensure there's an empty line at the end for new text
            
        
    def on_key(self, event): #Input handler
        if event.keysym in ("Left", "Right", "Up", "Down"): #TODO A lookup table
            if event.keysym == "Left":
                self.move_cursor("left")
            elif event.keysym == "Right":
                self.move_cursor("right")
            elif event.keysym == "Up": 
                self.move_cursor("up")
            elif event.keysym == "Down": 
                self.move_cursor("down")
            else:
                return
            self.render()
            return "break"
        
        if event.char.isprintable():
            for i, line in enumerate(self.text):
                if i == self.cursor_pos_y:
                    self.text[i] = (
                        line[: self.cursor_pos_x]
                        + event.char
                        + line[self.cursor_pos_x :]
                    )
            self.trailing_line()
            self.move_cursor("right")
            self.render()
            return "break"
        
        if event.keysym == "BackSpace" and self.cursor_pos_x > 0: #TODO handle line joins
            for i, line in enumerate(self.text):
                if i == self.cursor_pos_y:
                    self.text[i] = (
                        line[: self.cursor_pos_x - 1]
                        + line[self.cursor_pos_x :]
                    )
            self.move_cursor("left")
            self.render()
            return "break"  
        
        if event.keysym == "Return":
            pass


# --- basic window ---
root = tk.Tk()
editor = CustomEditor(root)
editor.pack(fill=tk.BOTH, expand=True) # expand frame to fill window
editor.pack()
root.mainloop()
