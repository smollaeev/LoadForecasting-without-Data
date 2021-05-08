import tkinter as tk
from components import MainWindow
from eventhandler import EventHandler
import subprocess
import matplotlib

event_handler = EventHandler ('./data')
root = tk.Tk ()
root.minsize (1300, 700)
root.tk.call ('wm', 'iconphoto', root._w, tk.PhotoImage(file='images/icon.png'))
root.title ("PAHBAR")
root.option_add ('*tearOff', False)
  
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

def get_uuid():
    return subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()

alowable_uuid = [
    'FDB26BB8-165E-11E3-834F-B6197F192822',
    '8EA4F82D-CB6D-9644-94E8-5E2674485912',
    '03A75C00-8BD9-11E2-9AC6-6C3BE523EB33',
    '4C4C4544-0037-5610-8046-B4C04F333632',
    '3DC50C85-7855-E311-8B14-742B6279BCE8', 
    '4E435451-384A-4E31-4134-40167E907719',
    '032E02B4-0499-0571-D906-FF0700080009',
    '33E4B79F-E95C-11E3-BE83-B8EE65C5AEE2',
    '03D502E0-045E-05D5-1606-190700080009',
    '031B021C-040D-05E1-B206-CE0700080009',
    '19CD3500-E8CF-11E3-ABC8-A0D3C125E328'
]
if get_uuid() in alowable_uuid:
    main_window = MainWindow(root, event_handler)
else:
    tk.Message(root, text= 'The licence is not valid').grid(column=0, row=0, padx=20, pady=20)

root.mainloop()