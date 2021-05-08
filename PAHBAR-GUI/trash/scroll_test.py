from tkinter import *
from tkinter import ttk

root = Tk()
spinval = StringVar()
days = ['Saturday', 'Sunday', 'Monday', 'Tuseday', 'Wednesday']
def change(*args):
    print(spinval.get())
s = ttk.Spinbox(root, values=days, textvariable=spinval, command=change).grid(column=0,row=0)
root.mainloop()