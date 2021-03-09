from datetime import date
import tkinter as tk
from tkinter import font
import tkinter.messagebox
import tkinter.filedialog
from tkinter import ttk
import os
from pathlib import Path
import subprocess
import copy
from typing import ChainMap


import jdatetime
from persiantools.jdatetime import JalaliDate

from eventhandler import Event
import queue

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotCanvas (ttk.LabelFrame):
    def __init__ (self, parent):
        super().__init__(parent, text = 'Figure', padding="3 3 12 12")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.language = 1

    def change_Language (self, language):
        self.language = language
        if language == 1:
            self.change_ToEnglish ()
        if language == 2:
            self.change_ToFarsi ()

    def change_ToEnglish (self):
        self.config (text= 'Figure')

    def change_ToFarsi (self):
        self.config (text= 'نمودار')

    def display_Figure (self, fig):
        canvas = FigureCanvasTkAgg (fig, master = self)
        canvas.get_tk_widget().grid (column=0,row=0)
        canvas.draw()
    
    def display_ErrorAttributes (self, errorAttributes):
        self.errorAttributes = ttk.Label (self, text = f'Mean Error:\n{"{:.2f}".format (errorAttributes [0])}%\nMaximum Error:\n{"{:.2f}".format (errorAttributes [1])}%\nHour:\n{errorAttributes [2]}', anchor = 'center', foreground = '#136b3c', background = '#f8f8f8',font = ('MS Reference Sans Serif', 12, 'bold'))
        self.errorAttributes.grid (column = 1, row = 0, padx = 5, pady = 5, sticky = 'w')
        # self.maxError = ttk.Label (self, text = f'', foreground = '#136b3c', background = '#f8f8f8',font = ('MS Reference Sans Serif', 6, 'bold'))
        # self.maxError.grid (column = 1, row = 1, padx = 5, pady = 5, sticky = 'e')
        # self.peakHourError = ttk.Label (self, text = f'', foreground = '#136b3c', background = '#f8f8f8',font = ('MS Reference Sans Serif', 6, 'bold'))
        # self.peakHourError.grid (column = 1, row = 2, padx = 5, pady = 5, sticky = 'e')

class DataTree(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding="3 3 12 12")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        tree = ttk.Treeview(self, selectmode='browse', height = 7)
        tree.grid(column=0,row=0)
        tree['show'] = 'headings'

        verscrlbar = ttk.Scrollbar(self,  
                           orient ="vertical",  
                           command = tree.yview)
        verscrlbar.grid(column=1,row=0,sticky=(tk.N,tk.S))
        tree.configure(yscrollcommand = verscrlbar.set)

        horscrlbar = ttk.Scrollbar(self,  
                           orient = "horizontal",  
                           command = tree.xview)
        horscrlbar.grid(column=0,row=1,sticky=(tk.W,tk.E))
        tree.configure(xscrollcommand = horscrlbar.set) 

        self.tree = tree
    
    def display_data(self, header_list, data_list, type = None):
        dataListCopy = copy.deepcopy (data_list)
        for i in range (len (dataListCopy)):
            for j in range (2, len (dataListCopy [i])):
                try:
                    dataListCopy [i][j] = "{:.2f}".format (dataListCopy [i][j])
                except:
                    continue

        tree = self.tree
        for row in tree.get_children():
            tree.delete(row)
        tree['columns'] = header_list
        for header in header_list:
            tree.heading(header,text=header, anchor='c')
            tree.column(header,width = 150, anchor ='c') 
        if type == None:
            i = 0
            for row in dataListCopy:
                i += 1
                if (i % 2 == 1):
                    tree.insert("", "end", values=row,tags = ('oddrow',))
                else:
                    tree.insert("", "end", values=row)             

            tree.tag_configure('oddrow', background='#baefda')

        if type == 'analysis':
            i = 0
            for row in dataListCopy:
                i += 1
                if (i % 3 == 0):
                    tree.insert("", "end", values=row,tags = ('Error',))
                else:
                    tree.insert("", "end", values=row)             

            tree.tag_configure('Error', background='#f3870c')
class DatePicker(ttk.LabelFrame):
    def __init__(self, parent, name, preDefinedDate = None):
        super().__init__(parent, text=name, padding="3 3 12 12")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(2, weight=1)

        year_var = tk.IntVar ()
        month_var = tk.IntVar ()
        day_var = tk.IntVar ()

        self.year_var = year_var
        self.month_var = month_var
        self.day_var = day_var

        self.yearLabel = ttk.Label(self, text='Year:', foreground = '#124d5d')
        self.yearLabel.config (font = ('MS Reference Sans Serif', 10, 'bold'))
        self.yearLabel.grid(column=0, row=0, sticky=(tk.E,),padx=5, pady=5)
        year_combo = ttk.Combobox(self, textvariable=year_var)
        year_combo.grid(column=1, row=0, sticky=(tk.E,),padx=5, pady=5)
        year_combo['values'] = tuple(range(1396, 1405))
        if preDefinedDate:
            year_var.set(preDefinedDate [0])
        else:
            year_var.set (year_combo['values'][0])
        year_combo.state(["readonly"])
        
        self.monthLabel = ttk.Label(self, text='Month:', foreground = '#124d5d')
        self.monthLabel.config (font = ('MS Reference Sans Serif', 10, 'bold'))
        self.monthLabel.grid(column=0, row=1, sticky=(tk.E,),padx=5, pady=5)
        month_combo = ttk.Combobox(self, textvariable=month_var)
        month_combo.grid(column=1, row=1, sticky=(tk.E,),padx=5, pady=5)
        month_combo['values'] = tuple(range(1, 13))
        month_combo.state(["readonly"])

        self.dayLabel = ttk.Label(self, text='Day:', foreground = '#124d5d')
        self.dayLabel.config (font = ('MS Reference Sans Serif', 10, 'bold'))
        self.dayLabel.grid(column=0, row=2, sticky=(tk.E,),padx=5, pady=5)
        day_combo = ttk.Combobox(self, textvariable=day_var)
        day_combo.grid(column=1, row=2, sticky=(tk.E,),padx=5, pady=5)
        if preDefinedDate:
            day_var.set (preDefinedDate [2])
        else:
            day_var.set (8)
        day_combo.state(["readonly"])


        def set_day_combo_values(*args):
            month = month_var.get()
            if 1 <= month <= 6:
                day_combo['values'] = tuple(range(1,32)) # 31 day month
            elif 7 <= month <= 11:
                day_combo['values'] = tuple(range(1,31)) # 30 day month
            else:
                if year_var.get() % 4 == 3: # kabise
                    day_combo['values'] = tuple(range(1,31)) # 30 day month
                else:
                    day_combo['values'] = tuple(range(1,30)) # 29 day month
            if str(day_var.get()) not in day_combo['values']:
                day_var.set(day_combo['values'][0])
        
        month_var.trace('w', set_day_combo_values)
        year_var.trace('w', set_day_combo_values)
        if preDefinedDate:
            month_var.set (preDefinedDate [1])
        else:
            month_var.set(month_combo['values'][0])

    def change_ToEnglish (self):
        self.yearLabel.config (text= 'Year', font = ('MS Reference Sans Serif', 10, 'bold'))
        self.monthLabel.config (text = 'Month', font = ('MS Reference Sans Serif', 10, 'bold'))
        self.dayLabel.config (text = 'Day', font = ('MS Reference Sans Serif', 10, 'bold'))

    def change_ToFarsi (self):
        self.yearLabel.config (text= 'سال', font = ('B Koodak Bold', 12, 'bold'))
        self.monthLabel.config (text= 'ماه', font = ('B Koodak Bold', 12, 'bold'))
        self.dayLabel.config (text= 'روز', font = ('B Koodak Bold', 12, 'bold'))

    def get_date(self):
        return jdatetime.date(
            self.year_var.get(),
            self.month_var.get(),
            self.day_var.get()
        ).togregorian()

class DataIO(ttk.LabelFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent, text='Data IO', padding="3 3 3 3")
        self.event_handler = event_handler
        self.language = 1

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.loadFileName = None

        buttonStyle = ttk.Style()
        buttonStyle.configure('my.TButton', font=('MS Reference Sans Serif', 12, 'bold'), foreground = '#466857')

        importedButtonStyle = ttk.Style ()
        importedButtonStyle.configure ('imported.TButton', font=('MS Reference Sans Serif', 12, 'bold'), foreground = '#45bd55')

        farsiButtonStyle = ttk.Style ()
        farsiButtonStyle.configure ('farsi.TButton', font=('B Koodak Bold', 14, 'bold'), foreground = '#466857')
        # buttonStyle.theme_use ('xpnative')

        # successfulLogo = tk.PhotoImage (file='images/successfulLogo.png')
        # self.successfulLogo = successfulLogo
        # unsuccessfulLogo = tk.PhotoImage (file='images/unsuccessfulLogo.png')
        # self.unsuccessfulLogo = unsuccessfulLogo

        s = ttk.Separator(self, orient=tk.HORIZONTAL)
        s.grid(column=0,row=2,sticky=(tk.E,tk.W,tk.N,))

        importLogo = tk.PhotoImage (file='images/importExcel.png')
        self.importLogo = importLogo
        self.import_button = ttk.Button(self, text='Import Load Data', command=self.import_fun, image = self.importLogo, compound= 'left', style = 'my.TButton')
        self.import_button.grid(column=0,row=0, padx=10, pady=2, sticky=(tk.E,tk.W,tk.N,) )

        exportLogo = tk.PhotoImage (file='images/exportExcel.png')
        self.exportLogo = exportLogo
        self.export_button = ttk.Button(self, text='Export Dataset', command=self.export_fun, image = self.exportLogo, compound = 'left', style = 'my.TButton')
        self.export_button.grid(column=0,row=1, padx=10, pady=2, sticky=(tk.E,tk.W,tk.N,))

        updateLogo = tk.PhotoImage (file='images/updateDataSet.png')
        self.updateLogo = updateLogo
        self.fetch_button = ttk.Button(self, text='Update Dataset', command=self.fetch_fun, image = self.updateLogo, compound = 'left', style = 'my.TButton')
        self.fetch_button.grid(column=0,row=3, padx=10, pady=2, sticky=(tk.E,tk.W,tk.N,))        

        editLogo = tk.PhotoImage (file='images/editDataSet.png')
        self.editLogo = editLogo       
        self.editButton = ttk.Button(self, text='Edit Dataset', command=self.edit_DataSet, image = self.editLogo, compound = 'left', style = 'my.TButton')
        self.editButton.grid(column=0,row=4, padx=10, pady=10, sticky=(tk.E,tk.W,tk.N,))

    def change_Language (self, language):
        self.language = language
        if language == 1:
            self.change_ToEnglish ()
        if language == 2:
            self.change_ToFarsi ()

    def change_ToFarsi (self):
        self.config (text= 'ورود و ذخیره داده‌ها')
        self.import_button.config (text= 'ورود اطلاعات بار', style= 'farsi.TButton')
        self.export_button.config (text= 'ذخیره دیتاست', style= 'farsi.TButton')
        self.fetch_button.config (text= 'تکمیل دیتاست', style= 'farsi.TButton')
        self.editButton.config (text= 'اصلاح دیتاست', style= 'farsi.TButton')

    def change_ToEnglish (self):
        self.config (text= 'Data IO')
        self.import_button.config (text= 'Import Load Data', style= 'my.TButton')
        self.export_button.config (text= 'Export Dataset', style= 'my.TButton')
        self.fetch_button.config (text= 'Update Dataset', style= 'my.TButton')
        self.editButton.config (text= 'Edit Dataset', style= 'my.TButton')
    
    def import_fun(self):
        files = [
            # ('All Files', '*.*'),  
            # ('Python Files', '*.py'), 
            # ('Text Document', '*.txt'),
            ('Excel Files', ['*.xlsx', '*.xls']),
        ]
        file_path = tk.filedialog.askopenfilename(filetypes = files, defaultextension = files)
        file_path = Path(file_path)
        path = Path(__file__)
        # print(Path(os.path.join(path.parent,'data')))
        # print(Path(os.path.join(path.parent,'data')).exists())
        # print(Path(os.path.join(path.parent,'data')).is_dir())
        # q = Path(os.path.join(path.parent,'data','sina.txt'))
        
        success = self.event_handler.handle(Event.IMPORT_DATA_BUTTON, file_path = file_path)
        if success:
            if self.language == 1:
                tkinter.messagebox.showinfo('Successful', 'Load data imported successfully!')
            if self.language == 2:
                tkinter.messagebox.showinfo ('عملیات موفق','اطلاعات بارگذاری شد!')
            self.loadFileName = os.path.basename(file_path)
            self.import_button.config (text= f"Imported File: \"{self.loadFileName}\"", style='imported.TButton')
    
    def export_fun(self):
        files = [
            # ('All Files', '*.*'),  
            # ('Python Files', '*.py'), 
            # ('Text Document', '*.txt'),
            ('Excel Files', '*.xlsx'),
        ]
        self.get_Mode ()
        file_path = tk.filedialog.asksaveasfilename(filetypes = files, defaultextension = files, initialfile = f'DataSet{self.mode[:-7]}')
        file_path = Path(file_path)
        success = self.event_handler.handle(Event.EXPORT_DATA_BUTTON, file_path = file_path)
        if success:
            if self.language == 1:
                tkinter.messagebox.showinfo('Successful', 'Dataset exported successfully!')
            if self.language == 2:
                tkinter.messagebox.showinfo('عملیات موفق', 'دیتاست ذخیره شد!')
            os.startfile (file_path)
        # else:
        #     if self.language == 1:
        #         tkinter.messagebox.showerror('Unsuccessful', 'Something went wrong!')
        #     if self.language == 2:
        #         tkinter.messagebox.showerror('ناموفق', 'متاسفانه مشکلی پیش آمده ... با پشتیبانی نرم‌افزار تماس بگیرید.')
    def get_Mode (self):
        self.mode = self.event_handler.get_Mode ()
        
    def fetch_fun(self):
        # self.progressBar.start ()
        success = self.event_handler.handle(Event.FETCH_ONLINE_DATA)
        if success:
            if isinstance (success, dict):
                if self.language == 1:
                    tkinter.messagebox.showerror ('Unsuccessful', success ['English'])
                if self.language == 2:
                    tkinter.messagebox.showerror ('Unsuccessful', success ['Farsi'])
            else:
                if self.language == 1:
                    tkinter.messagebox.showinfo('Successful', 'Dataset completed successfully!')
                if self.language == 2:
                    tkinter.messagebox.showinfo('عملیات موفق', 'دیتاست تکمیل شد!')
        else:
            if self.language == 1:
                tkinter.messagebox.showerror('Unsuccessful', 'Something went wrong!')
            if self.language == 2:
                tkinter.messagebox.showerror('ناموفق', 'متاسفانه مشکلی پیش آمده، در صورت اطمینان از صحیح بودن فرمت اطلاعات بارگذاری شده، با پشتیبانی نرم‌افزار تماس بگیرید.')

    # @staticmethod
    # def revive_updateLogo (fetch_button, updateLogo):
    #     fetch_button.config (image = updateLogo, compound = 'left')

    def edit_DataSet (self):
        if not (self.loadFileName):
            if self.language == 1:
                tkinter.messagebox.showerror('Unsuccessful', 'No correct load data imported!')
            if self.language == 2:
                tkinter.messagebox.showerror('ناموفق', 'اطلاعات بار وارد نشده است!')
        else:
            if self.language == 1:    
                response = tkinter.messagebox.askyesno (title="Edit DataSet", message=f"Are you sure you want to edit the dataset based on \"{self.loadFileName}\"? All previous data will be lost!")
            if self.language == 2:
                response = tkinter.messagebox.askyesno (title="اصلاح داده‌ها", message=f"آبا از اصلاح داده‌ها براساس فایل \"{self.loadFileName}\" اطمینان دارید? تمامی اطلاعات قبلی از دست خواهد رفت!")
            if response:
                success = self.event_handler.handle(Event.EDIT_DATA)
                if success:
                    if isinstance (success, dict):
                        if self.language == 1:
                            tkinter.messagebox.showerror('Unsuccessful', success ['English'])
                        if self.language == 2:
                            tkinter.messagebox.showerror('ناموفق', success ['Farsi'])
                    else:
                        if self.language == 1:
                            tkinter.messagebox.showinfo('Successful', 'Dataset edited successfully!')
                        if self.language == 2:
                            tkinter.messagebox.showinfo('عملیات موفق', 'اصلاحات انجام شد')
                else:
                    if self.language == 1:
                        tkinter.messagebox.showerror('Unsuccessful', 'Something went wrong!')
                    if self.language == 2:
                        tkinter.messagebox.showerror('ناموفق', 'متاسفانه مشکلی پیش آمده است ... در صورت اطمینان از فرمت داده‌های بارگذاری شده، با پشتیبانی نرم‌افزار تماس بگیرید')

class DataSetSelectionControl (ttk.Labelframe):
    def __init__(self,mainWindow, parent, event_handler):
        super().__init__(parent,text='Data Selection', padding="3 3 12 12")
        self.mainWindow = mainWindow
        self.event_handler = event_handler
        self.language = 1

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        for i in range (1, 4):
            self.columnconfigure(i, weight=1)

        self.mode = tk.StringVar (value='.pickle')
        self.determine_TrainEndDate ()
        self.get_LastTrainDate ()

        DGlogo = tk.PhotoImage (file='images/DG.png')
        self.DGlogo = DGlogo
        DGexcludedLogo = tk.PhotoImage (file = 'images/DG-Excluded.png')
        self.DGexcludedLogo = DGexcludedLogo
        calendarLogo = tk.PhotoImage (file = 'images/calendarLogo.png')
        self.calendarLogo = calendarLogo
        refreshLogo = tk.PhotoImage (file = 'images/refreshLogo.png')
        self.refreshLogo = refreshLogo
        

        self.radioButton1 = ttk.Radiobutton(self, text='Complete DataSet', variable=self.mode, value='.pickle',command=self.select_DataSet, image = self.DGlogo, compound = 'left')
        self.radioButton2 = ttk.Radiobutton(self, text='DG Excluded', variable=self.mode, value='_ExcludingDG.pickle',command=self.select_DataSet, image = self.DGexcludedLogo, compound = 'left')
        refreshButton = ttk.Button(self, command=self.update_EndDate, image = self.refreshLogo, compound = 'left')
        self.endDate = ttk.Label (self, text = f'Last Day in Dataset : {self.trainEndDate}\nTrained on {self.lastTrainDate}', foreground = '#136b3c', background = '#f8f8f8',font = ('MS Reference Sans Serif', 12, 'bold'))
        self.endDate.config (image = self.calendarLogo, compound = 'left')
        self.endDate.grid (column = 0, row = 0, padx = 1, pady = 1, sticky = 'w')
        refreshButton.grid (column = 1, row = 0, padx = 1, pady = 1, sticky = 'w')
        self.radioButton1.grid (column=2,row=0, padx=1, pady=1, sticky='w')
        self.radioButton2.grid (column=3,row=0, padx=1, pady=1, sticky='w')
        

    def determine_TrainEndDate (self):
        self.trainEndDate = self.event_handler.handle (Event.DETERMINE_TRAINENDDATE)
    
    def get_LastTrainDate (self):
        self.lastTrainDate = self.event_handler.handle (Event.GET_LAST_TRAIN_DATE)
    
    def update_EndDate (self):
        self.determine_TrainEndDate ()
        self.get_LastTrainDate ()
        if self.language == 1:
            self.endDate.config (text = f'Last Day in Dataset : {self.trainEndDate}\nTrained on {self.lastTrainDate}',font = ('MS Reference Sans Serif', 12, 'bold'))
        if self.language == 2:
            self.endDate.config (text = f'آخرین روز موجود در دیتاست: {self.trainEndDate}\nتاریخ آخرین آموزش: {self.lastTrainDate}', font = ('B Koodak Bold', 12, 'bold'))
    
    def select_DataSet (self):
        self.event_handler.handle (Event.DATA_DISPLAY_RADIO_BUTTON, mode = self.mode.get ())
        self.update_EndDate ()
        self.event_handler.handle (Event.REMOVE_FILE_PATH)
        self.event_handler.remove_AnalysisHistory ()
        self.mainWindow.revive_MainNoteBook ()

    def change_Language (self, language):
        self.language = language
        if (language == 1):
            self.change_ToEnglish ()

        if (language == 2):
            self.change_ToFarsi ()            

    def change_ToFarsi (self):
        self.config (text = 'انتخاب دیتاست')
        self.radioButton1.config (text= 'دیتاست کامل')
        self.radioButton2.config (text= 'دیتاست بدون نیروگاه')
        self.endDate.config (text = f'آخرین روز موجود در دیتاست: {self.trainEndDate}\nتاریخ آخرین آموزش: {self.lastTrainDate}', font = ('B Koodak Bold', 12, 'bold'))

    def change_ToEnglish (self):
        self.config (text = 'Data Selection')
        self.radioButton1.config (text='Complete DataSet')
        self.radioButton2.config (text='DG Excluded')
        self.endDate.config (text = f'Last Day in Dataset : {self.trainEndDate}\nTrained on {self.lastTrainDate}',font = ('MS Reference Sans Serif', 12, 'bold'))
        
class LanguageSelectionControl (ttk.Labelframe):
    def __init__(self,mainWindow, parent, dataSelection, mainNoteBook):
        super().__init__(parent,text='Language Selection', padding="3 3 12 12")
        self.mainWindow = mainWindow
        self.dataSelection = dataSelection
        self.mainNoteBook = mainNoteBook

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.mode = tk.IntVar (value=1)        

        radioButton1 = ttk.Radiobutton(self, text='English', variable=self.mode, value=1,command=self.select_Language)
        radioButton2 = ttk.Radiobutton(self, text='فارسی', variable=self.mode, value=2,command=self.select_Language)
        
        radioButton1.grid (column=0,row=0, padx=1, pady=1, sticky='w')
        radioButton2.grid (column=1,row=0, padx=1, pady=1, sticky='w')
    
    def select_Language (self):
        language = self.mode.get ()
        if language == 1:
            self.config (text= 'Language Selection')
        if language == 2:
            self.config (text= 'انتخاب زبان')
        
        self.dataSelection.change_Language (language)
        self.mainNoteBook.change_Language (language)

class DataDisplayControl(ttk.Labelframe):
    def __init__(self,parent, data_tree, event_handler, trainEndDate):
        super().__init__(parent,text='Data Display')

        style = ttk.Style()
        style.configure('Font.TLabelframe', font=('MS Reference Sans Serif', 10, 'bold'))
        
        self.config (style = "Font.TLabelframe")

        self.data_tree = data_tree
        self.event_handler = event_handler
        self.language = 1

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        from_date_picker = DatePicker(self,'From Date', preDefinedDate=[trainEndDate.year, trainEndDate.month, trainEndDate.day])
        self.from_date_picker = from_date_picker
        to_date_picker = DatePicker(self, 'To Date', preDefinedDate=[trainEndDate.year, trainEndDate.month, trainEndDate.day])
        self.to_date_picker = to_date_picker

        # self.mode = tk.StringVar (value='DataSet.pickle')
        # # checkButton = ttk.Checkbutton (self, text = 'Exclude DGs', command = self.checkButtonFunc)
        # radioButton1 = ttk.Radiobutton(self, text='Complete DataSet', variable=self.mode, value='DataSet.pickle',command=self.select_DataSet)
        # radioButton2 = ttk.Radiobutton(self, text='DGs Excluded', variable=self.mode, value='DataSet_ExcludingDG.pickle',command=self.select_DataSet)

        displayLogo = tk.PhotoImage (file='images/display.png')
        self.displayLogo = displayLogo
        self.displayButton = ttk.Button(self, text='Display Data', command=self.fun_wrapper, image = self.displayLogo, compound = 'left', style = 'my.TButton')

        deleteLogo = tk.PhotoImage (file = 'images/deleteLogo.png')
        self.deleteLogo = deleteLogo
        self.deleteButton = ttk.Button (self, text = 'Delete Data', command = self.delete_Row, image = self.deleteLogo, compound = 'left', style = 'my.TButton')
        
        from_date_picker.grid(column=0,row=0, padx=10, pady=10,sticky=(tk.E,tk.W,tk.N,tk.S))
        to_date_picker.grid(column=1,row=0, padx=10, pady=10,sticky=(tk.E,tk.W,tk.N,tk.S))
        # radioButton1.grid (column=0,row=1, padx=10, pady=10, sticky='w')
        # radioButton2.grid (column=0,row=2, padx=10, pady=10, sticky='w')
        self.displayButton.grid(column=0,row=1, padx=10, pady=10, sticky='w')
        self.deleteButton.grid (column = 1, row = 1, padx = 10, pady = 10, sticky = 'w')

    def change_Language (self, language):
        self.language = language
        if language == 1:
            self.change_ToEnglish ()
        if language == 2:
            self.change_ToFarsi ()

    def change_ToEnglish (self):
        self.config (text= 'Data Display')
        self.from_date_picker.change_ToEnglish ()
        self.to_date_picker.change_ToEnglish ()
        self.displayButton.config (text='Display Data', style = 'my.TButton')
        self.deleteButton.config (text = 'Delete Data', style= 'my.TButton')

    def change_ToFarsi (self):
        self.config (text= 'نمایش داده‌ها')
        self.from_date_picker.change_ToFarsi ()
        self.to_date_picker.change_ToFarsi ()
        self.displayButton.config (text= 'نمایش داده‌ها', style = 'farsi.TButton')
        self.deleteButton.config (text = 'حذف و جایگزینی با مقادیر پیش‌بینی شده', style= 'farsi.TButton')

    def get_period(self):
        return {
            'from_date': self.from_date_picker.get_date(),
            'to_date': self.to_date_picker.get_date()
        }
    
    def fun_wrapper(self):
        data_dict = self.event_handler.handle(Event.DISPLAY_DATA_BUTTON, **self.get_period())

        if not (data_dict ['data']):
            if self.language == 1:
                tkinter.messagebox.showerror('Unsuccessful', 'The range you selected is not available in the dataset!')
            if self.language == 2:
                tkinter.messagebox.showerror('ناموفق', 'بازه انتخاب شده در دیتاست موجود نیست')

        self.data_tree.display_data(data_dict['header'], data_dict['data'])

    def delete_Row (self):
        shamsiFromDate = JalaliDate (self.get_period() ['from_date'])
        shamsiToDate = JalaliDate (self.get_period () ['to_date'])
        if self.language == 1:
            response = tkinter.messagebox.askyesno (title="Delete Row", message=f"Are you sure you want to delete the selected data?\n\"From {shamsiFromDate} to {shamsiToDate}\"\nThe rows will be replaced by the predicted values ... ")
        if self.language == 2:
            response = tkinter.messagebox.askyesno (title="حذف داده و جایگزینی با پیش‌بینی", message=f"آیا از حذف داده انتخاب شده اطمینان دارید؟\n\"از تاریخ {shamsiFromDate} تا تاریخ  {shamsiToDate}\"\nداده‌های انتخاب شده با مقادیر پیش‌بینی جایگزین خواهند شد ")
        if response:
            success = self.event_handler.handle (Event.DELETE_ROW, **self.get_period())
            if success:
                if isinstance (success, dict):
                    if self.language == 1:
                        tkinter.messagebox.showerror('Unsuccessful', success ['English'])
                    if self.language == 2:
                        tkinter.messagebox.showerror('ناموفق', success ['Farsi'])
                else:
                    if self.language == 1:
                        tkinter.messagebox.showinfo('Successful', 'Dataset edited successfully!')
                    if self.language == 2:
                        tkinter.messagebox.showinfo('عملیات موفق', 'دیتاست اصلاح شد!')
            else:
                if self.language == 1:
                    tkinter.messagebox.showerror('Unsuccessful', 'Something went wrong! Please check the selected date and try again!')
                if self.language == 2:
                    tkinter.messagebox.showerror('ناموفق', 'متاسفانه مشکلی پیش آمده است! در صورتی که از وجود بازه انتخاب شده در دیتاست اطمینان دارید، با پشتیبانی نرم‌افزار تماس بگیرید')

class PredictionDisplayControl(ttk.Labelframe):
    def __init__(self,parent, data_tree, event_handler, trainEndDate):
        super().__init__(parent,text='Prediction Display')
        self.data_tree = data_tree
        self.event_handler = event_handler
        self.language = 1

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        from_date_picker = DatePicker(self,'From Date', preDefinedDate=[trainEndDate.year, trainEndDate.month, trainEndDate.day + 2])
        self.from_date_picker = from_date_picker
        to_date_picker = DatePicker(self, 'To Date', preDefinedDate=[trainEndDate.year, trainEndDate.month, trainEndDate.day + 2])
        self.to_date_picker = to_date_picker

        predictLogo = tk.PhotoImage (file='images/predict.png')
        self.predictLogo = predictLogo
        self.display_button = ttk.Button(self, text='Predict', command=self.fun_wrapper, image = self.predictLogo, compound = 'left', style = 'my.TButton')

        exportLogo = tk.PhotoImage (file='images/exportPrediction.png')
        self.exportLogo = exportLogo
        self.export_button = ttk.Button(self, text='Export Results', command=self.export_fun, image = self.exportLogo, compound = 'left', style = 'my.TButton')
        
        from_date_picker.grid(column=0,row=0, padx=10, pady=10,sticky=(tk.E,tk.W,tk.N,tk.S))
        to_date_picker.grid(column=1,row=0, padx=10, pady=10,sticky=(tk.E,tk.W,tk.N,tk.S))
        self.display_button.grid(column=0,row=1, padx=10, pady=10, sticky='W')
        self.export_button.grid(column=1,row=1, padx=10, pady=10, sticky='W')

    def change_Language (self, language):
        self.language = language
        if language == 1:
            self.change_ToEnglish ()
        if language == 2:
            self.change_ToFarsi ()

    def change_ToEnglish (self):
        self.config (text = 'Prediction Display')
        self.from_date_picker.change_ToEnglish ()
        self.to_date_picker.change_ToEnglish ()
        self.display_button.config (text='Predict', style= 'my.TButton')
        self.export_button.config (text= 'Export Results', style= 'my.TButton')

    def change_ToFarsi (self):
        self.config (text = 'نمایش نتایج پیش‌بینی')
        self.from_date_picker.change_ToFarsi ()
        self.to_date_picker.change_ToFarsi ()
        self.display_button.config (text = 'پیش‌بینی', style= 'farsi.TButton')
        self.export_button.config (text= 'ذخیره نتایج', style= 'farsi.TButton')

    def get_period(self):
        return {
            'from_date': self.from_date_picker.get_date(),
            'to_date': self.to_date_picker.get_date()
        }
    def fun_wrapper(self):
        predictDates = self.event_handler.determine_PredictDates (**self.get_period())
        if self.language == 1:
            response = tkinter.messagebox.askyesno (title="Predict Dates", message=f"Load will be predicted for the following dates ... If it is correct click yes, unless click No and complete your dataset!\nFrom {JalaliDate (predictDates [0])} to {JalaliDate (predictDates [-1])}\nIs it correct?")
        if self.language == 2:
            rightAligned = f"با توجه به آخرین تاریخ موجود در دیتاست، تاریخ‌های زیر پیش‌بینی خواهد شد ...\nاز تاریخ {JalaliDate(predictDates[0])} تا تاریخ {JalaliDate (predictDates [-1])}\nدر صورت صحت بازه انتخاب شده، بر روی گزینه Yes کلیک کنید!"
            response = tkinter.messagebox.askyesno (title="تاریخ‌های پیش‌بینی", message= "{rightAligned:>}".format (rightAligned = rightAligned))
        if response:
            data_dict = self.event_handler.handle(Event.DISPLAY_PREDICTION_BUTTON,**self.get_period())
            if data_dict:
                if data_dict == 1:
                    if self.language == 1:
                        tkinter.messagebox.showerror('Unsuccessful', 'Invalid date!')
                    if self.language == 2:
                        tkinter.messagebox.showerror('ناموفق', 'تاریخ انتخاب شده معتبر نیست')

                if isinstance (data_dict, dict):
                    if 'English' in data_dict:
                        if self.language == 1:
                            tkinter.messagebox.showerror('Unsuccessful', data_dict ['English'])
                        if self.language == 2:
                            tkinter.messagebox.showerror('ناموفق', data_dict ['Farsi'])
                    else:
                        if self.language == 1:
                            tkinter.messagebox.showinfo('Successful', 'Load predicted successfully!') 
                        if self.language == 2:
                            tkinter.messagebox.showinfo('عملیات موفق', 'پیش‌بینی انجام شد') 
                        self.data_tree.display_data(data_dict['header'], data_dict['data'])
            else:
                if self.language == 1:
                    tkinter.messagebox.showerror('Unsuccessful', 'Somethiong went wrong!')
                if self.language == 2:
                    tkinter.messagebox.showerror('ناموفق', 'متاسفانه مشکلی پیش آمده است ... با پشتیبانی نرم‌افزار تماس بگیرید')
                

    def export_fun(self):
        files = [
            # ('All Files', '*.*'),  
            # ('Python Files', '*.py'), 
            # ('Text Document', '*.txt'),
            ('Excel Files', '*.xlsx'),
        ]
        dates = self.get_period()
        fromDateShamsi = JalaliDate (dates ['from_date'])
        toDateShamsi = JalaliDate (dates ['to_date'])
        self.get_Mode ()
        file_path = tk.filedialog.asksaveasfilename (filetypes = files, defaultextension = files, initialfile = f'Prediction{self.mode [:-7]}_ from {fromDateShamsi} to {toDateShamsi}')
        file_path = Path(file_path)
        success = self.event_handler.handle(Event.EXPORT_Prediction_BUTTON, **dates, file_path = file_path)
        if success:
            if self.language == 1:
                tkinter.messagebox.showinfo('Successful', 'Prediction results exported successfully!')
            if self.language == 2:
                tkinter.messagebox.showinfo('عملیات موفق', 'نتایج پیش‌بینی ذخیره شد')
            os.startfile (file_path)
        else:
            if self.language == 1:
                tkinter.messagebox.showerror('Unsuccessful', 'Predicted load information is not available!')
            if self.language == 2:
                tkinter.messagebox.showerror('ناموفق', 'اطلاعات پیش‌بینی در دسترس نیست')

    def get_Mode (self):
        self.mode = self.event_handler.get_Mode ()

class AnalysisDisplayControl(ttk.Labelframe):
    def __init__(self,parent, data_tree, plotCanvas, event_handler, trainEndDate):
        super().__init__(parent,text='Analysis Display')
        self.data_tree = data_tree
        self.plotCanvas = plotCanvas
        self.event_handler = event_handler
        self.language = 1

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        from_date_picker = DatePicker(self,'From Date', preDefinedDate= [trainEndDate.year, trainEndDate.month, trainEndDate.day])
        self.from_date_picker = from_date_picker
        to_date_picker = DatePicker(self, 'To Date', preDefinedDate = [trainEndDate.year, trainEndDate.month, trainEndDate.day])
        self.to_date_picker = to_date_picker

        analyzeLogo = tk.PhotoImage (file='images/analysisLogo.png')
        self.analyzeLogo = analyzeLogo
        self.analyzeButton = ttk.Button(self, text='Analyze Prediction', command=self.analyze_Prediction, image = self.analyzeLogo, compound = 'left', style = 'my.TButton')

        exportLogo = tk.PhotoImage (file='images/exportAnalysis.png')
        self.exportLogo = exportLogo
        self.export_button = ttk.Button(self, text='Export Results', command=self.export_fun, image = self.exportLogo, compound = 'left', style = 'my.TButton')

        plotLogo = tk.PhotoImage (file='images/plotLogo.png')
        self.plotLogo = plotLogo
        self.plotButton = ttk.Button(self, text='Plot Results', command=self.plot_Results, image = self.plotLogo, compound = 'left', style = 'my.TButton')

        savePlotLogo = tk.PhotoImage (file='images/savePlotLogo.png')
        self.savePlotLogo = savePlotLogo
        self.savePlotButton = ttk.Button(self, text='Save Plot', command=self.save_Plot, image = self.savePlotLogo, compound = 'left', style = 'my.TButton')
        
        from_date_picker.grid(column=0,row=0, padx=10, pady=10,sticky=(tk.E,tk.W,tk.N,tk.S))
        to_date_picker.grid(column=1,row=0, padx=10, pady=10,sticky=(tk.E,tk.W,tk.N,tk.S))
        self.analyzeButton.grid(column=0,row=1, padx=5, pady=5, sticky='W')
        self.export_button.grid(column=0,row=2, padx=5, pady=5, sticky='W')
        self.plotButton.grid(column=1,row=1, padx=5, pady=5, sticky='W')
        self.savePlotButton.grid(column=1,row=2, padx=5, pady=5, sticky='W')

    def change_Language (self, language):
        self.language = language
        if language == 1:
            self.change_ToEnglish ()
        if language == 2:
            self.change_ToFarsi ()

    def change_ToEnglish (self):
        self.config (text='Analysis Display')
        self.from_date_picker.change_ToEnglish ()
        self.to_date_picker.change_ToEnglish ()
        self.analyzeButton.config (text='Analyze Prediction', style='my.TButton')
        self.export_button.config (text='Export Results', style='my.TButton')
        self.plotButton.config (text='Plot Results', style='my.TButton')
        self.savePlotButton.config (text= 'Save Plot', style = 'my.TButton')

    def change_ToFarsi (self):
        self.config (text='نمایش نتایج آنالیز پیش‌بینی')
        self.from_date_picker.change_ToFarsi ()
        self.to_date_picker.change_ToFarsi ()
        self.analyzeButton.config (text='آنالیز پیش‌بینی', style='farsi.TButton')
        self.export_button.config (text='ذخیره نتایج آنالیز', style='farsi.TButton')
        self.plotButton.config (text='رسم نمودار', style='farsi.TButton')
        self.savePlotButton.config (text= 'ذخیره نمودار', style = 'farsi.TButton')

    def get_period(self):
        return {
            'from_date': self.from_date_picker.get_date(),
            'to_date': self.to_date_picker.get_date()
        }

    def analyze_Prediction (self):
        data_dict = self.event_handler.handle(Event.ANALYZE_PREDICTION,**self.get_period())
        if data_dict:
            if isinstance (data_dict, dict):
                if 'English' in data_dict:
                    if self.language == 1:
                        tkinter.messagebox.showerror('Unsuccessful', data_dict ['English'])
                    if self.language == 2:
                        tkinter.messagebox.showerror('ناموفق', data_dict ['Farsi'])
                else:
                    if self.language == 1:
                        tkinter.messagebox.showinfo ('Successful', 'Analysis completed successfully!') 
                    if self.language == 2:
                        tkinter.messagebox.showinfo ('عملیات موفق', 'آنالیز پیش‌بینی انجام شد')
                    self.data_tree.display_data (data_dict['header'], data_dict['data'], type = 'analysis')
        else:
            if self.language == 1:
                tkinter.messagebox.showerror('Unsuccessful', 'Analysis failed!')
            if self.language == 2:
                tkinter.messagebox.showerror('ناموفق', 'متاسفانه مشکلی پیش آمده است! با پشتیبانی نرم‌افزار تماس بگیرید')

    def plot_Results (self):
        fig = self.event_handler.handle(Event.PLOT_RESULTS,**self.get_period())
        if fig:
            if isinstance (fig, dict):
                if self.language == 1:
                    tkinter.messagebox.showerror('Unsuccessful', fig ['English'])
                if self.language == 2:
                    tkinter.messagebox.showerror('ناموفق', fig ['Farsi'])
            else:
                if self.language == 1:
                    tkinter.messagebox.showinfo ('Successful', 'Plots prepared successfully!') 
                if self.language == 2:
                    tkinter.messagebox.showinfo ('عملیات موفق', 'رسم نمودارها تکمیل شد') 
                self.plotCanvas.display_Figure (fig)
                self.display_MaxAndMean ()
        else:
            if self.language == 1:
                tkinter.messagebox.showerror('Unsuccessful', 'Failed!')
            if self.language == 2:
                tkinter.messagebox.showerror('ناموفق', 'متاسفانه مشکلی پیش آمده است ... لطفاً با پشتیبانی تماس بگیرید')

    def display_MaxAndMean (self):
        errorAttributes = self.event_handler.handle(Event.CALCULATE_ERRORATTRIBUTES)
        self.plotCanvas.display_ErrorAttributes (errorAttributes)

    def export_fun(self):
        files = [
            # ('All Files', '*.*'),  
            # ('Python Files', '*.py'), 
            # ('Text Document', '*.txt'),
            ('Excel Files', '*.xlsx'),
        ]
        dates = self.get_period ()
        fromDateShamsi = JalaliDate (dates ['from_date'])
        toDateShamsi = JalaliDate (dates ['to_date'])
        self.get_Mode ()
        file_path = tk.filedialog.asksaveasfilename (filetypes = files, defaultextension = files, initialfile = f'Analysis{self.mode [:-7]}_ from {fromDateShamsi} to {toDateShamsi}')
        file_path = Path(file_path)
        success = self.event_handler.handle(Event.EXPORT_ANALYSIS_RESULTS, file_path = file_path)
        if success:
            if self.language == 1:
                tkinter.messagebox.showinfo('Successful', 'Analysis results exported successfully!')
            if self.language == 2:
                tkinter.messagebox.showinfo('عملیات موفق', 'نتایج آنالیز ذخیره شد')
            os.startfile (file_path)
        else:
            if self.language == 1:
                tkinter.messagebox.showerror('Unsuccessful', 'Analysis results are not available!')
            if self.language == 2:
                tkinter.messagebox.showerror('ناموفق', 'نتایج آنالیز در دسترس نیست')

    def save_Plot (self):
        files=[
        ('JPEG', ('*.jpg', '*.jpeg', '*.jpe')), ('PNG', '*.png')]
        dates = self.get_period ()
        toDateShamsi = JalaliDate (dates ['to_date'])
        self.get_Mode ()
        file_path = tk.filedialog.asksaveasfilename(filetypes = files, defaultextension = files, initialfile = f'AnalysisPlot{self.mode [:-7]}_{toDateShamsi}')
        file_path = Path(file_path)
        success = self.event_handler.handle(Event.SAVE_ANALYSIS_PLOT, file_path = file_path)
        if success:
            if self.language == 1:
                tkinter.messagebox.showinfo('Successful', 'Analysis plot exported successfully!')
            if self.language == 2:
                tkinter.messagebox.showinfo('عملیات موفق', 'نمودارها ذخیره شد')
            os.startfile (file_path)
        else:
            if self.language == 1:
                tkinter.messagebox.showerror('Unsuccessful', 'Try "Plot Results" first!')
            if self.language == 2:
                tkinter.messagebox.showerror('ناموفق', 'لازم است ابتدا نمودارها رسم شوند')

    def get_Mode (self):
        self.mode = self.event_handler.get_Mode ()

class DataNote(ttk.Frame):
    def __init__(self,parent, event_handler, trainEndDate):
        super().__init__(parent)
        self.event_handler = event_handler
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(2, weight=1)
           
        self.data_io = DataIO(self, self.event_handler)
        self.data_io.grid(column=2,row=0, rowspan = 2, padx=10, pady=10, sticky=(tk.E,tk.W,tk.N,tk.S))

        data_tree = DataTree(self)
        data_tree.grid(column=0,row=2,columnspan=3,padx=10, pady=10, sticky=(tk.E,tk.W,tk.N,tk.S))
        self.data_display_control = DataDisplayControl(self, data_tree, event_handler, trainEndDate)
        self.data_display_control.grid(column=0,row=0,columnspan =2 , rowspan = 2, padx=10, pady=10, sticky=(tk.E,tk.W,tk.N,tk.S))

    def change_Language (self, language):
        self.data_io.change_Language (language)
        self.data_display_control.change_Language (language)

class HistoryControl (ttk.LabelFrame):
    def __init__ (self, parent, root, event_handler):
        super().__init__(parent, text='History', padding="3 3 3 3")
        self.event_handler = event_handler
        self.root = root
        self.language = 1

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        exportHistoryLogo = tk.PhotoImage (file='images/exportExcel.png')
        self.exportHistoryLogo = exportHistoryLogo
        exportButton = ttk.Button(self, text='Export History', command=self.export_History, image = self.exportHistoryLogo, compound = 'left', style = 'my.TButton')
        exportButton.grid(column=0,row=0, columnspan=2, padx=10, pady=10, sticky='WE')
        self.exportButton = exportButton

    def change_Language (self, language):
        self.language = language
        if language == 1:
            self.change_ToEnglish ()
        if language == 2:
            self.change_ToFarsi ()
    
    def change_ToEnglish (self):
        self.config (text= 'History')
        self.exportButton.config (text='Export History', style = 'my.TButton')

    def change_ToFarsi (self):
        self.config (text= 'تاریخچه پیش‌بینی')
        self.exportButton.config (text='ذخیره تاریخچه پیش‌بینی', style = 'farsi.TButton')
    
    def export_History (self):
        files = [
            # ('All Files', '*.*'),  
            # ('Python Files', '*.py'), 
            # ('Text Document', '*.txt'),
            ('Excel Files', '*.xlsx'),
        ]
        self.get_Mode ()
        file_path = tk.filedialog.asksaveasfilename(filetypes = files, defaultextension = files, initialfile = f'PredictionHistory{self.mode [:-7]}')
        file_path = Path(file_path)
        success = self.event_handler.handle(Event.EXPORT_HISTORY_BUTTON, file_path = file_path)
        if success:
            if self.language == 1:
                tkinter.messagebox.showinfo('Successful', 'Prediction history exported successfully!')
            if self.language == 2:
                tkinter.messagebox.showinfo('عملیات موفق', 'تاریخچه پیش‌بینی ذخیره شد')
            os.startfile (file_path)
        else:
            if self.language == 1:
                tkinter.messagebox.showerror('Unsuccessful', 'No prediction history!')
            if self.language == 2:
                tkinter.messagebox.showerror('ناموفق', 'تاریخچه پیش‌بینی موجود نیست')

    def get_Mode (self):
        self.mode = self.event_handler.get_Mode ()
            
class PredictControl(ttk.LabelFrame):
    def __init__(self, parent, root, event_handler):
        super().__init__(parent, text='Prediction Engine', padding="3 3 3 3")
        self.event_handler = event_handler
        self.root = root
        self.language = 1

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        trainLogo = tk.PhotoImage (file='images/train.png')
        self.trainLogo = trainLogo
        train_button = ttk.Button(self, text='Train', command=self.predict, image = self.trainLogo, compound = 'left', style = 'my.TButton')
        train_button.grid(column=0,row=0, columnspan=2, padx=10, pady=10, sticky='WE')
        self.train_button = train_button
        status_var = tk.StringVar()
        self.status_var = status_var
        self.statusLabel = ttk.Label(self, text='Status: ', foreground = '#124d5d')
        self.statusLabel.config (font = ('MS Reference Sans Serif', 12, 'bold'))
        self.statusLabel.grid(column=0, row=1, sticky=(tk.W,),padx=10, pady=5)
        status_var.set('Not Working')
        tk.Label(self, textvariable=status_var).grid(column=1, row=1, sticky=(tk.W,),padx=0, pady=5)
        self.queue = queue.Queue()

    def change_Language (self, language):
        self.language = language
        if language == 1 :
            self.change_ToEnglish ()
        if language == 2:
            self.change_ToFarsi ()

    def change_ToEnglish (self):
        self.config (text='Prediction Engine')
        self.train_button.config (text='Train', style = 'my.TButton')
        self.statusLabel.config (text='Status: ', font = ('MS Reference Sans Serif', 12, 'bold'))

    def change_ToFarsi (self):
        self.config (text='موتور پیش‌بینی')
        self.train_button.config (text='آموزش مدل', style = 'farsi.TButton')
        self.statusLabel.config (text='وضعیت: ', font = ('B Koodak Bold', 14, 'bold'))
        
    def process_queue(self):
        try:
            msg = self.queue.get(0)
            self.train_button.state(['!disabled'])
            self.status_var.set('Not Working')
        except queue.Empty:
            self.root.after(1000, self.process_queue)
    
    def predict(self):
        self.train_button.state(['disabled'])
        self.status_var.set('Working ...')
        self.event_handler.handle(Event.TRAIN_BUTTON ,queue =self.queue)
        self.root.after(1000, self.process_queue)

class PredictionNote(ttk.Frame):
    def __init__(self,parent, root, event_handler, trainEndDate):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(2, weight=1)
        self.event_handler = event_handler
        
        # data_selection_control = DataSetSelectionControl (self, event_handler)
        # data_selection_control.grid (column = 0, row = 0, padx=10, pady=10,sticky=(tk.E,tk.W,tk.N,tk.S))
        data_tree = DataTree(self)
        data_tree.grid(column=0,row=2,columnspan=3,padx=10, pady=10,sticky=(tk.E,tk.W,tk.N,tk.S))
        self.prediction_display_control = PredictionDisplayControl(self, data_tree, self.event_handler, trainEndDate)
        self.prediction_display_control.grid(column=0,row=0, rowspan = 2, columnspan = 2, sticky=(tk.E,tk.W,tk.N,tk.S), padx=10, pady=10)
        self.historyControl = HistoryControl (self, root, self.event_handler)
        self.historyControl.grid (column = 2, row = 0, sticky=(tk.E,tk.W,tk.N,tk.S), padx=10, pady=10)
        self.prediction_control = PredictControl(self, root, self.event_handler)
        self.prediction_control.grid(column=2,row=1, sticky=(tk.E,tk.W,tk.N,tk.S), padx=10, pady=10) 

    def change_Language (self, language):
        self.prediction_display_control.change_Language (language)
        self.historyControl.change_Language (language)
        self.prediction_control.change_Language (language)

class AnalysisNote(ttk.Frame):
    def __init__(self,parent, root, event_handler, trainEndDate):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        # self.rowconfigure(3, weight=1)
        self.event_handler = event_handler

        data_tree = DataTree(self)
        data_tree.grid(column=0,row=2,columnspan=4,padx=10, pady=10,sticky=(tk.E,tk.W,tk.N,tk.S))
        self.plotCanvas = PlotCanvas (self)
        self.plotCanvas.grid(column=1,row=0,rowspan = 2, columnspan=3,padx=10, pady=10,sticky=(tk.E,tk.W,tk.N,tk.S))
        self.analysisDisplayControl = AnalysisDisplayControl(self, data_tree, self.plotCanvas, self.event_handler, trainEndDate)
        self.analysisDisplayControl.grid (column=0,row=0, rowspan = 2, sticky=(tk.E,tk.W,tk.N,tk.S), padx=5, pady=5)

    def change_Language (self, language):
        self.plotCanvas.change_Language (language)
        self.analysisDisplayControl.change_Language (language)

class MainNoteBook(ttk.Notebook):
    def __init__(self,parent, root, event_handler, trainEndDate):
        super().__init__(parent)
        self.event_handler = event_handler

        self.data_note = DataNote(self, self.event_handler, trainEndDate)
        self.data_note.grid(sticky='ewns')
        self.add(self.data_note, text='Data')

        self.shortTermPredictionNote = PredictionNote(self, root, self.event_handler, trainEndDate)
        self.shortTermPredictionNote.grid(sticky=(tk.E,tk.W,tk.N,tk.S))
        self.add(self.shortTermPredictionNote, text='Short-Term Prediction')

        self.longTermPredictionNote = PredictionNote(self, root, self.event_handler, trainEndDate)
        self.longTermPredictionNote.grid(sticky=(tk.E,tk.W,tk.N,tk.S))
        self.add(self.longTermPredictionNote, text='Long-Term Prediction')

        self.analysisNote = AnalysisNote (self, root, self.event_handler, trainEndDate)
        self.analysisNote.grid (sticky=(tk.E,tk.W,tk.N,tk.S))
        self.add (self.analysisNote, text='Analysis')

    def change_Language (self, language):
        self.data_note.change_Language (language)
        self.shortTermPredictionNote.change_Language (language)
        self.longTermPredictionNote.change_Language (language)
        self.analysisNote.change_Language (language)

class MainWindow():
    def __init__(self, parent, event_handler):
        self.parent = parent
        self.event_handler = event_handler        
         
        image = tk.PhotoImage(file='images/header.png')
        
        self.image  = image # it is added to anchor image to prevent garbage collection
        header = tk.Label(parent)
        header['image'] = image
        header.grid(column=0, row=0, columnspan = 2, sticky=(tk.E,tk.W,tk.N,tk.S))

        self.dataSelection = DataSetSelectionControl (self, parent, event_handler)
        self.dataSelection.grid (column = 0, row = 1, sticky=(tk.E,tk.W,tk.N,tk.S))

        main_notebook = MainNoteBook(parent, parent,self.event_handler, self.dataSelection.trainEndDate)
        main_notebook.grid(column=0, row=2, columnspan = 2, sticky=(tk.E,tk.W,tk.N,tk.S))
        menuBar = tk.Menu (parent)
        parent.config (menu = menuBar)
        help_ = tk.Menu (menuBar)
        menuBar.add_cascade (menu = help_, label = 'Help') 
        help_.add_command (label = 'Documentation', command = self.open_Documentation)

        self.languageSelection = LanguageSelectionControl (self, parent, self.dataSelection, main_notebook)
        self.languageSelection.grid (column = 1, row = 1, sticky=(tk.E,tk.W,tk.N,tk.S))

    def open_Documentation (self):
        self.event_handler.handle (Event.DOCUMENTATION)

    def revive_MainNoteBook (self):
        main_notebook = MainNoteBook(self.parent, self.parent,self.event_handler, self.dataSelection.trainEndDate)
        main_notebook.grid(column=0, row=2, columnspan = 2, sticky=(tk.E,tk.W,tk.N,tk.S)) 
        self.languageSelection = LanguageSelectionControl (self, self.parent, self.dataSelection, main_notebook)
        self.languageSelection.grid (column = 1, row = 1, sticky=(tk.E,tk.W,tk.N,tk.S))       