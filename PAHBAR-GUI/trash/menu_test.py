from tkinter import *
from tkinter import messagebox

def donothing():
   filewin = Toplevel(root)
   button = Button(filewin, text="Do nothing button")
   button.pack()
def f():
    '''
    this is a funtion
    '''
    print('Hiii')

root = Tk()
root.option_add('*tearOff', FALSE)
menubar = Menu(root)
sysmenu = Menu(menubar, name='system')
menubar.add_cascade(menu=sysmenu)
filemenu = Menu(menubar)
filemenu.add_command(label="New", command=donothing)
filemenu.entryconfigure('New', state=DISABLED)
filemenu.add_command(label="Open", command=f, accelerator="Control")
filemenu.add_command(label="Save", command=donothing)
filemenu.entryconfigure(2, state=DISABLED)
filemenu.add_command(label="Save as...", command=donothing)
filemenu.add_command(label="Close", command=lambda: root.event_generate("<<OpenFindDialog>>"))

def launchFindDialog(*args):
    messagebox.showinfo(message="بنده امیدوارم پیدا کنی ")
    
root.bind("<<OpenFindDialog>>", launchFindDialog)

filemenu.add_separator()
recent_files = Menu(filemenu)
for i in range(5):
    recent_files.add_command(label = str(i))
check = StringVar()
filemenu.add_checkbutton(label='Check', variable=check, onvalue=1, offvalue=0)
radio = StringVar()
filemenu.add_radiobutton(label='One', variable=radio, value=1)

filemenu.add_cascade(menu= recent_files, label="recent files")
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

root.config(menu=menubar)
root.mainloop()