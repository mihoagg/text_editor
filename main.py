import tkinter as tk
from tkinter import font
from enum import Enum, auto

# TODO: 
# line wrapping
# clipboard support, ctrl cvax
# text highlight
# undo redo stack
# mouse support for cursor movement and text selection
# scrolbar
# i/o
# scroll when moving cursor out of view DONE
# cursor renders on top padding DONE

# maybe single index for cursor position instead of (x, y)




# wishlist / future features:
# INPUT LAYER:
# Scrolling and copy paste, undo redo, mouse support
# TEXT LAYOUT LAYER:
# Line wrapping 
# Syntax highlighting, bidi text, complex scripts


# RENDERING LAYER:
# Smooth scrolling, hardware acceleration
# Plugin system for rendering (eg. minimap, line numbers, etc.)
# Syntax Highlighting


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

class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()
    LINE_START = auto()
    LINE_END = auto()
    
class CustomEditor(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        # --- canvas ---
        self.canvas = tk.Canvas(self, width=600, height=200, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-1>", self.on_left_click_debug)
        
        
        # --- font & metrics ---
        self.editor_font = font.Font(family="Courier New", size=16)
        self.char_width = self.editor_font.measure("M")
        self.line_height = self.editor_font.metrics("linespace")
        self.ascent = self.editor_font.metrics("ascent")
        self.descent = self.editor_font.metrics("descent")

        # --- document state ---
        self.text = "Hello World\nThis is a sample text\nEach line is separated by a newline character\nPython handles this using \\n\na\nb\nc\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\nend"
        self.cursor_x_index = 0  # position of the cursor in the text
        self.cursor_y_index = 0
        self.preferred_cursor_x = self.cursor_x_index  # for vertical movements
        
        # --- layout constants ---
        self.left_padding = 10
        self.top_padding = 20
        self.baseline_y = self.top_padding + self.ascent - self.descent # baseline position accounting for tkinter anchor

        # --- scroll state ---
        '''
        viewport, content, scrollbar
        scroll position, scroll offset (scroll_y), render offset, clamp to content size
        
        mayber overscan
        
        '''
        self.scroll_y = 0  # vertical scroll offset
        self.line_start_index = 0  
        self.line_end_index = 0
        self.visible_line_count = 0 
        self.overscan_lines = 2
        
        
        # --- bindings ---
        self.bind_all("<Key>", self.on_key)
                
        # --- initial setup ---
        self.text = self.parse_text()
        self.trailing_line()
        self.calculate_visible_lines()
        
        # initial draw
        self.render()
        
    def calculate_visible_lines(self): 
        view_top = self.scroll_y
        view_bottom = self.scroll_y + self.canvas.winfo_height()
        self.line_start_index = view_top // self.line_height
        self.line_end_index = (view_bottom + self.line_height - 1) // self.line_height #First line outside viewport
        # print("before overscan:", self.line_start_index, self.line_end_index)
        # print("last line", self.text[self.line_end_index -1])
                
        #clamp to bounds
        self.line_start_index = max(0, self.line_start_index - self.overscan_lines)
        self.line_end_index = min(len(self.text), self.line_end_index + self.overscan_lines)
        
        #visible line count
        self.visible_line_count = self.line_end_index - self.line_start_index - 1 #inclusive
        
    def draw_debug_scrollline(self): 
        # Convert line indices to canvas Y coordinates
        y_start = (
            self.line_start_index * self.line_height
            - self.scroll_y
            + self.top_padding
            + self.ascent
        )
        
        y_end = (
            (self.line_end_index - 1) * self.line_height
            - self.scroll_y
            - self.line_height
            + self.baseline_y
        )

        # Draw a vertical debug line on the left side
        self.canvas.create_line(
            self.left_padding, y_start,
            self.left_padding, y_end,
            fill="red",
            width=2,
            tags="debug"
        )
        
        #draw a horizontal line at the last line
        self.canvas.create_line(
            0, y_end,
            600, y_end,
            fill="blue",
            width=2,
            tags="debug"
        )
        
        self.canvas.create_line(
            0, y_start,
            600, y_end,
            fill="blue",
            width=2,
            tags="debug"
        )
    
    def draw_debug_frame(self):
        self.canvas.create_rectangle(
            self.left_padding,
            self.line_start_index * self.line_height - self.scroll_y + self.top_padding - self.descent,
            600,
            (self.line_end_index - 1) * self.line_height - self.scroll_y + self.top_padding,
        )
    
    def parse_text(self):
        # split text into lines based on newline characters
        lines = self.text.split("\n")
        return lines
    
    def on_canvas_resize(self, event):
        self.calculate_visible_lines()
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
    
    def trailing_line(self):
        if self.text[-1] != "":
            self.text.append("")  # ensure there's an empty line at the end for new text    
    
    def render(self):
        self.canvas.delete("all")
        
        # debug lines
        # self.draw_debug_baselines()
        # self.draw_debug_scrollline()
        # self.draw_debug_frame()
        
        
        # text
        y = self.top_padding + self.ascent + (self.line_start_index * self.line_height) - self.scroll_y
        for line in range(self.line_start_index, self.line_end_index):
            x = self.left_padding
            for ch in self.text[line]:
                self.canvas.create_text(
                    x, y,
                    text=ch,
                    font=self.editor_font,
                    anchor="sw"
                )
                x += self.char_width
            y += self.line_height
                    
        # cursor
        cursor_x = self.left_padding + self.cursor_x_index * self.char_width
        cursor_y = self.top_padding - self.descent + self.cursor_y_index * self.line_height - self.scroll_y
        self.canvas.create_line(
            cursor_x, cursor_y,
            cursor_x, cursor_y + self.ascent + self.descent,
            fill="black",
        )
    
    
    # cursor movement
    def move_cursor(self, direction: Direction):
        if direction == Direction.LEFT:
            if self.cursor_x_index > 0:
                self.cursor_x_index -= 1
            elif self.cursor_x_index == 0 and self.cursor_y_index > 0:
                self.cursor_y_index -= 1
                self.cursor_x_index = len(self.text[self.cursor_y_index])
            self.normalize_cursor_position()
            self.preferred_cursor_x = self.cursor_x_index
        elif direction == Direction.RIGHT:
            if self.cursor_x_index == len(self.text[self.cursor_y_index]):
                self.cursor_y_index += 1
                self.cursor_x_index = 0
            else: 
                self.cursor_x_index += 1
            self.normalize_cursor_position()
            self.preferred_cursor_x = self.cursor_x_index
        elif direction == Direction.UP:
            self.cursor_y_index -= 1
            self.normalize_cursor_position(use_preferred=True)
        elif direction == Direction.DOWN:
            self.cursor_y_index += 1
            self.normalize_cursor_position(use_preferred=True)
        elif direction == Direction.LINE_START:
            self.cursor_x_index = 0
            self.normalize_cursor_position()
            self.preferred_cursor_x = self.cursor_x_index
        elif direction == Direction.LINE_END:
            line = self.text[self.cursor_y_index]
            self.cursor_x_index = len(line)
            self.normalize_cursor_position()
            self.preferred_cursor_x = self.cursor_x_index
        #cursor debug
        # cursor_y = self.top_padding - self.descent + self.cursor_y_index * self.line_height - self.scroll_y
        # print("cursor_y:", cursor_y)
        self.keep_cursor_in_view()

    def normalize_cursor_position(self, use_preferred: bool = False):
        # Vertical bounds
        self.cursor_y_index = max(self.cursor_y_index, 0)
        self.cursor_y_index = min(self.cursor_y_index, len(self.text) - 1)   
        
        line = self.text[self.cursor_y_index] # current line after vertical normalization to avoid index errors
        
        # Horizontal bounds
        if use_preferred:
            self.cursor_x_index = min(self.preferred_cursor_x, len(line))
        else:
            self.cursor_x_index = max(self.cursor_x_index, 0)
            self.cursor_x_index = min(self.cursor_x_index, len(line))      
    
    def keep_cursor_in_view(self):
        view_top_y = 0
        view_bottom_y =self.canvas.winfo_height()
        cursor_y = self.top_padding - self.descent + self.cursor_y_index * self.line_height - self.scroll_y
        scroll_offset = 0
        if cursor_y < view_top_y:  
            scroll_offset = view_top_y - cursor_y
            self.move_scroll(-scroll_offset)
        if cursor_y + self.line_height > view_bottom_y:
            scroll_offset = (cursor_y + self.line_height) - view_bottom_y
            self.move_scroll(scroll_offset)
        # implement scroll adjustment, measure how much out of view to scroll by
        
        
    
    # input handling        
    def on_key(self, event):
        movement_keys = {
            "Left": Direction.LEFT,
            "Right": Direction.RIGHT,
            "Up": Direction.UP,
            "Down": Direction.DOWN,
            "Home": Direction.LINE_START,
            "End": Direction.LINE_END
        }
        if event.keysym in movement_keys:
            self.move_cursor(movement_keys[event.keysym])
            self.render()
            return "break"
        
        if event.char.isprintable() and len(event.char) == 1:
            for i, line in enumerate(self.text):
                if i == self.cursor_y_index:
                    self.text[i] = (
                        line[: self.cursor_x_index]
                        + event.char
                        + line[self.cursor_x_index :]
                    )
            self.trailing_line()
            self.move_cursor(Direction.RIGHT)
            self.render()
            return "break"
        
        if event.keysym == "BackSpace":
            text_after_cursor = ""
            if self.cursor_x_index > 0:
                for i, line in enumerate(self.text):
                    if i == self.cursor_y_index:
                        text_after_cursor = line[self.cursor_x_index :]
                        self.text[i] = (
                            line[: self.cursor_x_index - 1] + line[self.cursor_x_index :]
                        )                        
            elif self.cursor_x_index == 0:
                text_after_cursor = self.text[self.cursor_y_index][self.cursor_x_index :]
                for i, line in enumerate(self.text):
                    if i == self.cursor_y_index:
                        self.text.pop(i)
            self.move_cursor(Direction.LEFT)
            for i, line in enumerate(self.text):
                if i == self.cursor_y_index:
                    self.text[i] = (
                        line + text_after_cursor
                    )
            self.render()
            return "break"
        
        if event.keysym == "Delete":
            pass
        
        if event.keysym == "Return":
            for i,line in enumerate(self.text):
                if i == self.cursor_y_index:
                    new_line = line[self.cursor_x_index :]
                    self.text[i] = line[: self.cursor_x_index]
                    self.text.insert(i + 1, new_line)
            self.move_cursor(Direction.DOWN)
            self.move_cursor(Direction.LINE_START)
            self.render()
            return "break"
            
    # mouse wheel scrolling
    def on_mousewheel(self, event):
        if event.delta:
            self.move_scroll(-1 * (event.delta // 120) * self.line_height) 
            self.render()
            # print("mousewheel moved and rendered")
            return "break"
        
    def move_scroll(self, delta_y: int):
        self.scroll_y += delta_y
        self.scroll_y = max(0, self.scroll_y)
        max_scroll = max(0, len(self.text) * self.line_height - self.canvas.winfo_height())
        self.scroll_y = min(self.scroll_y, max_scroll)
        self.calculate_visible_lines()  
        
        #cursor debug
        # cursor_y = self.top_padding - self.descent + self.cursor_y_index * self.line_height - self.scroll_y
        # print("cursor_y:", cursor_y)
        
        # print("scroll_y:", self.scroll_y)
        # print("first visible line:", self.first_visible_line)
        # print("last visible line:", self.last_visible_line)
        # print("visible line count:", self.visible_line_count) 
        
    # mouse debugging
    def on_left_click_debug(self, event):
        print("click at:", event.x, event.y)
        if event.y >= self.line_start_index * self.line_height - self.scroll_y + self.top_padding and event.y <= (self.line_end_index - 1) * self.line_height - self.scroll_y + self.top_padding:
            print("within rendered lines")
        else:
            print("outside rendered lines")

# --- basic window ---
root = tk.Tk()
editor = CustomEditor(root)
editor.pack(fill=tk.BOTH, expand=True) # expand frame to fill window
editor.pack()
root.mainloop()
