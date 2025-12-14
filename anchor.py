import tkinter as tk

root = tk.Tk()

canvas = tk.Canvas(root, width=300, height=200, bg="white")
canvas.pack()

# reference point
canvas.create_oval(95, 95, 105, 105, fill="red")

canvas.create_text(100, 100, text="Hello", anchor="sw", fill="blue")


root.mainloop()
