import customtkinter as ctk

from set_up import LoginApp


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('600x300')
        self.entry = ctk.CTkEntry(self,)
        self.entryy = ctk.CTkEntry(self)
        self.button = ctk.CTkButton(self, text='  Play',command=self.click)
        self.button.grid(row=0, column=14,padx=41,pady=10)
        self.button = ctk.CTkButton(self, text='  Stats', command=self.click, fg_color='grey')
        self.button.grid(row = 1, column=14,padx=41,pady=10)
        self.button = ctk.CTkButton(self, text='  Exit ', command=self.exit_app,fg_color='red')
        self.button.grid(row = 2, column=14,padx=41,pady=10)
        self.mainloop()

    def click(self):
        app=LoginApp()
        app.mainloop()
    def exit_app(self):
        app=LoginApp()
        app.quit()

main_window = MainWindow()