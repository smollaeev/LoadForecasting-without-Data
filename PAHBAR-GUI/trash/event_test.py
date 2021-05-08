from tkinter import *
from tkinter import ttk
root = Tk()
button = ttk.Button(root, text='Okay')
button.grid(column=1, row=1)
button.state(['disabled'])
parent = root
measureSystem = StringVar()
def metricChanged():
    print(measureSystem.get())
check = ttk.Checkbutton(root, text='Use Metric', 
	    command=metricChanged, variable=measureSystem,
	    onvalue='metric', offvalue='imperial')
check.grid(column=1,row=2)

username = StringVar()
name = ttk.Entry(parent, textvariable=username)
name.grid(column=1, row=3)
def username_change(*args):
    print(username.get())



username.trace_add("write", username_change)

countryvar = StringVar()
country = ttk.Combobox(parent, textvariable=countryvar)
country.grid(column=1, row=3)
country['values'] = ('USA', 'Canada', 'Australia')
country.state(["readonly"])
def combo_fun(*args):
    country.selection_clear()
    print(country.get())
country.bind('<<ComboboxSelected>>', combo_fun)
country.grid(column=2, row=4)

phone = StringVar()
def phoneChange():
    print(phone.get())
home = ttk.Radiobutton(root, text='Home', variable=phone,command=phoneChange ,value='home').grid(column=2, row=2)
office = ttk.Radiobutton(root, text='Office', variable=phone,command=phoneChange, value='office').grid(column=3, row=2)
cell = ttk.Radiobutton(root, text='Mobile', variable=phone, command=phoneChange, value='cell').grid(column=4, row=2)


l =ttk.Label(root, text="Starting...")
image = PhotoImage(file='Figure_1.png')
l['image'] = image
l['compound'] = 'center'
l['font'] = 'TkFixedFont'
l.grid(column=2, row=1)
l.bind('<Enter>', lambda e: l.configure(text='Moved mouse inside'))
l.bind('<Leave>', lambda e: l.configure(text='Moved mouse outside'))
l.bind('<ButtonPress-1>', lambda e: l.configure(text='Clicked left mouse button'))
l.bind('<3>', lambda e: l.configure(text='Clicked right mouse button'))
l.bind('<Double-1>', lambda e: l.configure(text='Double clicked'))
l.bind('<B3-Motion>', lambda e: l.configure(text='right button drag to %d,%d' % (e.x, e.y)))
root.mainloop()