from __future__ import annotations
import tkinter as tk
from tkinter import font
from enum import Enum, auto


# TODO: 
# split input and delete into document layer
# mouse support for cursor movement and text selection
# # line wrapping
# clipboard support, ctrl cvax
# text highlight
# undo redo stack
# scrolbar
# i/o

# minimize redraw (render whole line, dirty region, caching)
# use data structure for text storage
# observer pattern

# scroll when moving cursor out of view DONE
# cursor renders on top padding DONE

# modularize:
# maybe split render to draw_text and draw_cursor
# split on_key to movement, insertion, backspace return...

# maybe single index for cursor position instead of (x, y)




class EditorContext:
    def __init__(self):
        self.canvas = None
        self.renderer = None
        self.document = None
        self.scroll = None
        self.input = None
        
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
        self.canvas = tk.Canvas(self, width=600, height=400, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # --- components ---
        self.ctx = EditorContext()
        self.ctx.renderer = Renderer(self.ctx)
        self.ctx.document = DocumentModel(self.ctx)
        self.ctx.scroll = ScrollManager(self.ctx)
        self.ctx.input = InputManager(self.ctx)
        self.ctx.canvas = self.canvas
        
        # --- bindings ---
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<MouseWheel>", self.ctx.input.on_mousewheel)
        self.canvas.bind("<Button-1>", self.ctx.input.on_leftclick)
        self.bind_all("<Key>", self.ctx.input.on_key)
        
        # --- bindings ---
        #self.bind_all("<Key>", self.on_key)
        
        # initial set up
        self.ctx.document.lines = self.ctx.document.parse_text()
        self.ctx.document.trailing_line()
        self.ctx.scroll.calculate_visible_lines()
        self.ctx.renderer.render()

    def on_canvas_resize(self, event):
        self.ctx.scroll.calculate_visible_lines()
        self.ctx.renderer.render()

class Renderer:
    def __init__(self, ctx: EditorContext):
        self.ctx = ctx
        
        # --- font & metrics ---
        self.editor_font = font.Font(family="Courier New", size=16)
        self.char_width = self.editor_font.measure("M")
        self.line_height = self.editor_font.metrics("linespace")
        self.ascent = self.editor_font.metrics("ascent")
        self.descent = self.editor_font.metrics("descent")
                
        # --- layout constants ---
        self.left_padding = 10
        # self.top_padding = 20
        
    def render_text(self):
        # text
        y = (self.ctx.scroll.line_start_index * self.line_height) - self.ctx.scroll.scroll_y
        self.ctx.canvas.create_line(0, y, 500, y, fill="black")
        for line in range(self.ctx.scroll.line_start_index, self.ctx.scroll.line_end_index):
            x = self.left_padding
            for ch in self.ctx.document.lines[line]:
                self.ctx.canvas.create_text(
                    x, y,
                    text=ch,
                    font=self.editor_font,
                    anchor="nw"
                )
                x += self.char_width
            y += self.line_height
    
    def render_cursor(self): #TODO fix top padding
        # cursor
        cursor_x = self.left_padding + self.ctx.document.cursor_x_index * self.char_width
        cursor_y = self.ctx.document.cursor_y_index * self.line_height - self.ctx.scroll.scroll_y
        self.ctx.canvas.create_line(
            cursor_x, cursor_y,
            cursor_x, cursor_y + self.line_height,
            fill="black",
        ) 
    
    def render(self):
        self.ctx.canvas.delete("all") 
        self.render_text()
        self.render_cursor()
        
class DocumentModel:
    def __init__(self, ctx: EditorContext):
        self.ctx = ctx
        self.text = "Hello World\nThis is a sample text\nEach line is separated by a newline character\nPython handles this using \\n\na\nb\nc\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\nend"
        self.lines = []
        self.cursor_x_index = 0  # position of the cursor in the text
        self.cursor_y_index = 0
        self.preferred_cursor_x = self.cursor_x_index
        
    def parse_text(self):
        # split text into lines based on newline characters
        lines = self.text.split("\n")
        return lines
    
    def trailing_line(self):
        if self.lines[-1] != "":
            self.lines.append("")  # ensure there's an empty line at the end for new text  
    
    def get_line_number(self):
        return len(self.lines)
    
    def move_cursor(self, direction: Direction):
        if direction == Direction.LEFT:
            if self.cursor_x_index > 0:
                self.cursor_x_index -= 1
            elif self.cursor_x_index == 0 and self.cursor_y_index > 0:
                self.cursor_y_index -= 1
                self.cursor_x_index = len(self.lines[self.cursor_y_index])
            self.normalize_cursor_position()
            self.preferred_cursor_x = self.cursor_x_index
        elif direction == Direction.RIGHT:
            if self.cursor_x_index == len(self.lines[self.cursor_y_index]):
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
            line = self.lines[self.cursor_y_index]
            self.cursor_x_index = len(line)
            self.normalize_cursor_position()
            self.preferred_cursor_x = self.cursor_x_index
        self.ctx.scroll.keep_cursor_in_view()
        
    def normalize_cursor_position(self, use_preferred: bool = False):
        # Vertical bounds
        self.cursor_y_index = max(self.cursor_y_index, 0)
        self.cursor_y_index = min(self.cursor_y_index, self.get_line_number() - 1)   
        
        line = self.lines[self.cursor_y_index] # current line after vertical normalization to avoid index errors
        
        # Horizontal bounds
        if use_preferred:
            self.cursor_x_index = min(self.preferred_cursor_x, len(line))
        else:
            self.cursor_x_index = max(self.cursor_x_index, 0)
            self.cursor_x_index = min(self.cursor_x_index, len(line))    
    
    def insert_at_cursor(self):
        pass
         
    def delete_at_cursor(self):
        text_after_cursor = ""
        if self.cursor_x_index > 0:
            current_line = self.lines[self.cursor_y_index]
            text_after_cursor = current_line[self.cursor_x_index :]
            current_line = current_line[: self.cursor_x_index - 1] + current_line[self.cursor_x_index :]
            self.lines[self.cursor_y_index] = current_line
            self.move_cursor(Direction.LEFT)
        
        elif self.cursor_x_index == 0 and self.cursor_y_index > 0:
            current_line = self.lines[self.cursor_y_index]
            text_after_cursor = current_line[self.cursor_x_index :]
            previous_line = self.lines[self.cursor_y_index - 1]
            # merge lines
            previous_line = previous_line + text_after_cursor
            #move cursor
            self.move_cursor(Direction.LEFT)
            #update buffer
            self.lines[self.cursor_y_index] = previous_line
            #delete line
            self.lines.pop(self.cursor_y_index + 1)
            #recalculate visable lines
            self.ctx.scroll.calculate_visible_lines()
            
            
        elif self.cursor_x_index == 0 and self.cursor_y_index == 0:
            pass
        
    def move_cursor_to_mouse(self, mouse_x, mouse_y): 
        #calculate which line clicked
        self.cursor_y_index = (mouse_y + self.ctx.scroll.scroll_y) // self.ctx.renderer.line_height
        #which char is clicked
        self.cursor_x_index = (mouse_x - self.ctx.renderer.left_padding) // self.ctx.renderer.char_width
        #relative x within the character
        relative_x = (mouse_x - self.ctx.renderer.left_padding) % self.ctx.renderer.char_width
        if relative_x > self.ctx.renderer.char_width / 2:
            # place cursor after this character
            self.cursor_x_index += 1
        self.normalize_cursor_position()  
        self.ctx.scroll.keep_cursor_in_view()
        
class ScrollManager: 
    def __init__(self, ctx: EditorContext):
        self.ctx = ctx
        # --- scroll state ---
        self.scroll_y = 0  # vertical scroll offset
        self.line_start_index = 0  
        self.line_end_index = 0
        self.visible_line_count = 0 
        self.overscan_lines = 2

    def calculate_visible_lines(self): 
        view_top = self.scroll_y
        view_bottom = self.scroll_y + self.ctx.canvas.winfo_height()
        self.line_start_index = view_top // self.ctx.renderer.line_height
        self.line_end_index = (view_bottom + self.ctx.renderer.line_height - 1) // self.ctx.renderer.line_height #First line outside viewport
        # print("before overscan:", self.line_start_index, self.line_end_index)
        # print("last line", self.ctx.document.lines[self.line_end_index -1])
                
        #clamp to bounds
        self.line_start_index = max(0, self.line_start_index - self.overscan_lines)
        self.line_end_index = min(self.ctx.document.get_line_number(), self.line_end_index + self.overscan_lines)
        
        #visible line count
        self.visible_line_count = self.line_end_index - self.line_start_index - 1 #inclusive

    def move_scroll(self, delta_y: int):
        self.scroll_y += delta_y
        self.scroll_y = max(0, self.scroll_y)
        max_scroll = max(0, self.ctx.document.get_line_number() * self.ctx.renderer.line_height - self.ctx.canvas.winfo_height())
        self.scroll_y = min(self.scroll_y, max_scroll)
        self.calculate_visible_lines()  
        
    def keep_cursor_in_view(self):
        view_top_y = 0
        view_bottom_y =self.ctx.canvas.winfo_height()
        cursor_y = self.ctx.document.cursor_y_index * self.ctx.renderer.line_height - self.scroll_y
        scroll_offset = 0
        if cursor_y < view_top_y:  
            scroll_offset = view_top_y - cursor_y
            self.move_scroll(-scroll_offset)
        if cursor_y + self.ctx.renderer.line_height > view_bottom_y:
            scroll_offset = (cursor_y + self.ctx.renderer.line_height) - view_bottom_y
            self.move_scroll(scroll_offset)
        
class InputManager:
    def __init__(self, ctx: EditorContext):
        self.ctx = ctx      
        
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
            self.ctx.document.move_cursor(movement_keys[event.keysym])
            self.ctx.renderer.render()
            return "break"
        
        if event.char.isprintable() and len(event.char) == 1: #TODO split logic into document
            for i, line in enumerate(self.ctx.document.lines):
                if i == self.ctx.document.cursor_y_index:
                    self.ctx.document.lines[i] = (
                        line[: self.ctx.document.cursor_x_index]
                        + event.char
                        + line[self.ctx.document.cursor_x_index :]
                    )
            self.ctx.document.trailing_line()
            self.ctx.document.move_cursor(Direction.RIGHT)
            self.ctx.renderer.render()
            return "break"
        
        if event.keysym == "BackSpace":
            self.ctx.document.delete_at_cursor()
            self.ctx.renderer.render()
            return "break" 
        
        if event.keysym == "Delete":
            pass  
        
        if event.keysym == "Return": #TODO split logic into document
            for i,line in enumerate(self.ctx.document.lines):
                if i == self.ctx.document.cursor_y_index:
                    new_line = line[self.ctx.document.cursor_x_index :]
                    self.ctx.document.lines[i] = line[: self.ctx.document.cursor_x_index]
                    self.ctx.document.lines.insert(i + 1, new_line)
            self.ctx.document.move_cursor(Direction.DOWN)
            self.ctx.document.move_cursor(Direction.LINE_START)
            self.ctx.renderer.render()
            return "break"  
        
    def on_mousewheel(self, event):
        if event.delta:
            self.ctx.scroll.move_scroll(-1 * (event.delta // 120) * self.ctx.renderer.line_height) 
            self.ctx.renderer.render()
            # print("mousewheel moved and rendered")
            return "break"
        
    def on_leftclick(self, event):
        self.ctx.document.move_cursor_to_mouse(event.x, event.y)
        self.ctx.renderer.render()
        return "break" 
        

# --- basic window ---
root = tk.Tk()
editor = CustomEditor(root)
editor.pack(fill=tk.BOTH, expand=True) # expand frame to fill window
editor.pack()
root.mainloop()

    