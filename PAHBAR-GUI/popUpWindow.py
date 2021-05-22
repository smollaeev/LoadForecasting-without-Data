from tkinter import *
class popupWindow(object):
    def __init__(self, master, text, numberOfEntries, labelOfEntries):
        top = self.top = Toplevel(master)
        self.label = Label (top,text=text)
        self.label.grid ()
        self.get_entries (numberOfEntries, labelOfEntries)
        self.button=Button (top, text='Ok', command=self.cleanup)
        self.b.pack()

    def get_entries (self, numberOfEntries, labelOfEntries):
        self.entries = []
        for i in range (numberOfEntries):
            self.entries.append (Entry (self.top))
            self.entries [i].grid ()

    def cleanup(self):
        self.value = self.e.get()
        self.top.destroy()