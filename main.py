from __future__ import annotations
import tkinter as tk
from tkinter import font
from enum import Enum, auto


# TODO: 
# snap cursor after selection
# create editor state class that store scroll, cursor, selection, and undo redo
# split input and delete into document layer
# mouse support for cursor movement and text selection
# line wrapping
# clipboard support, ctrl cvax
# text highlight
# undo redo stack
# scrolbar
# i/o

# minimize redraw (render whole line, dirty region, caching , only move index onscroll, non rerender highlight)
# use data structure for text storage
# observer pattern

# scroll when moving cursor out of view DONE
# cursor renders on top padding DONE

# modularize:
# maybe split render to draw_text and draw_cursor DONE
# split on_key to movement, insertion, backspace return...

# maybe single index for cursor position instead of (x, y)


'''
on click: -set anchor,
on drag: -set active,
-normalize start end by compare y first then x if y1 = y2 ,
-update document state with derived start and end,
-call render,
'''



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
        self.canvas.bind("<B1-Motion>", self.ctx.input.on_left_drag)
        self.bind_all("<Key>", self.ctx.input.on_key)
        
        # initial set up
        self.ctx.document.lines = self.ctx.document.parse_text()
        self.ctx.document.trailing_line()

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
        y = (self.ctx.scroll.line_start_index * self.line_height) - self.ctx.scroll.scroll_y
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
    
    def render_cursor(self):
        if self.ctx.document.cursor_y_index in range(self.ctx.scroll.line_start_index, self.ctx.scroll.line_end_index):
            cursor_x = self.left_padding + self.ctx.document.cursor_x_index * self.char_width
            cursor_y = self.ctx.document.cursor_y_index * self.line_height - self.ctx.scroll.scroll_y
            self.ctx.canvas.create_line(
                cursor_x, cursor_y,
                cursor_x, cursor_y + self.line_height,
                fill="black",
            ) 

    def render_select(self):
        anchor_x, anchor_y = self.ctx.document.selection_index['anchor']
        active_x, active_y = self.ctx.document.selection_index['active']
        
        #normalize start end index
        line_start = min(anchor_y, active_y)
        line_end   = max(anchor_y, active_y)
        
        if anchor_y == active_y:
            column_start = min(anchor_x, active_x)
            column_end   = max(anchor_x, active_x)
        elif anchor_y < active_y:
            column_start = anchor_x
            column_end   = active_x
        else:
            column_start = active_x
            column_end   = anchor_x
        
        for line in range(line_start, line_end):
            if line in range(self.ctx.scroll.line_start_index, self.ctx.scroll.line_end_index):
                # selection in only 1 line
                if line == line_start and line == line_end - 1:
                    self.ctx.canvas.create_rectangle(
                        #x1
                        column_start * self.char_width + self.left_padding,
                        #y1
                        line * self.line_height - self.ctx.scroll.scroll_y,
                        #x2
                        column_end * self.char_width + self.left_padding,
                        #y2
                        line * self.line_height - self.ctx.scroll.scroll_y + self.line_height,
                        fill="#CCE8FF",
                        outline=""
                    )
                # line at start index
                elif line == line_start:
                    self.ctx.canvas.create_rectangle(
                        #x1
                        column_start * self.char_width + self.left_padding,
                        #y1
                        line * self.line_height - self.ctx.scroll.scroll_y,
                        #x2
                        len(self.ctx.document.lines[line]) * self.char_width + self.left_padding,
                        #y2
                        line * self.line_height - self.ctx.scroll.scroll_y + self.line_height,
                        fill="#CCE8FF",
                        outline=""
                    )
                # line at end index 
                # - 1 for line_end is exclusive
                elif line == line_end - 1:
                    self.ctx.canvas.create_rectangle(
                        #x1
                        self.left_padding,
                        #y1
                        line * self.line_height - self.ctx.scroll.scroll_y,
                        #x2
                        column_end * self.char_width + self.left_padding,
                        #y2
                        line * self.line_height - self.ctx.scroll.scroll_y + self.line_height,
                        fill="#CCE8FF",
                        outline=""
                    )
                #else print the whole line
                else:
                    self.ctx.canvas.create_rectangle(
                        #x1
                        self.left_padding,
                        #y1
                        line * self.line_height - self.ctx.scroll.scroll_y,
                        #x2
                        len(self.ctx.document.lines[line]) * self.char_width + self.left_padding,
                        #y2
                        line * self.line_height - self.ctx.scroll.scroll_y + self.line_height,
                        fill="#CCE8FF",
                        outline=""
                    )
    
    # def move_selected_area(self):
    #     pass
    
    def render(self):
        self.ctx.canvas.delete("all") 
        if self.ctx.document.selection_index['anchor'] is not None and self.ctx.document.selection_index['active'] is not None:
            self.render_select()
        self.render_text()
        self.render_cursor()
        
class DocumentModel:
    def __init__(self, ctx: EditorContext):
        self.ctx = ctx
        self.text = "Hello World\nThis is a sample text\nEach line is separated by a newline character\nPython handles this using \\n\na\nb\nc\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\na\nend"
        self.lines = []
        #TODO: reformat cursor index
        self.cursor_x_index = 0  # position of the cursor in the text
        self.cursor_y_index = 0
        self.preferred_cursor_x = self.cursor_x_index
        #selection
        self.selection_index = {
            'anchor': (0,0), #x,y
            'active': (5,1), #exclusive end index
            #'direction': ""
            }

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
    
    def insert_at_cursor(self, ch):
        line = self.lines[self.cursor_y_index]
        self.lines[self.cursor_y_index] = (
                line[: self.cursor_x_index]
                + ch
                + line[self.cursor_x_index :]
            )
        self.trailing_line()
        self.move_cursor(Direction.RIGHT)
         
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
            
            
        elif self.cursor_x_index == 0 and self.cursor_y_index == 0: #TODO delete if line empty
            pass
        
    def move_cursor_to_mouse(self, mouse_x, mouse_y): 
        self.cursor_x_index, self.cursor_y_index = self.coords_to_index(
        mouse_x, mouse_y + self.ctx.scroll.scroll_y
        )
        self.normalize_cursor_position()  
        self.ctx.scroll.keep_cursor_in_view()
    
    # raw pixels to text index
    def coords_to_index(self, x=0, y=0):
        line_index = y // self.ctx.renderer.line_height
        line_index = min(max(line_index, 0), len(self.lines) - 1)
        column_index = (x - self.ctx.renderer.left_padding) // self.ctx.renderer.char_width
        column_index = min(max(column_index, 0), len(self.lines[line_index]))
        # check if cursor is past half a character
        char_start_x = self.ctx.renderer.left_padding + column_index * self.ctx.renderer.char_width
        if x - char_start_x > self.ctx.renderer.char_width / 2:
            column_index += 1
            column_index = min(column_index, len(self.lines[line_index]))
        return column_index, line_index
        
    def screen_coords_to_index(self, screen_x=0, screen_y=0):
        doc_x = screen_x
        doc_y = screen_y + self.ctx.scroll.scroll_y
        return self.coords_to_index(doc_x, doc_y)
    
    def set_selection(self, cursor_x, cursor_y):
        column, line = self.screen_coords_to_index(cursor_x, cursor_y)
        if self.selection_index['anchor'] is None:
            self.selection_index['anchor'] = (column, line)
        self.selection_index['active'] = (column, line + 1)
        self.move_cursor_to_mouse(cursor_x, cursor_y)
        
    def clear_selection(self):
        # Clear previous selection
        self.selection_index['anchor'] = None
        self.selection_index['active'] = None
        
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
        
        if event.char.isprintable() and len(event.char) == 1: 
            self.ctx.document.insert_at_cursor(event.char)
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
            return "break"
        
    def on_leftclick(self, event):
        self.ctx.document.move_cursor_to_mouse(event.x, event.y)
        self.ctx.document.clear_selection()
        self.ctx.renderer.render()
        return "break" 
        
    def on_left_drag(self, event): #TODO
        self.ctx.document.set_selection(event.x, event.y)
        self.ctx.renderer.render()
        return "break"
        
# --- basic window ---
root = tk.Tk()
editor = CustomEditor(root)
editor.pack(fill=tk.BOTH, expand=True) # expand frame to fill window
editor.pack()
root.mainloop()

    