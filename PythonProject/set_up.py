from customtkinter import *

from main_game import LoginApp1

class LoginApp(CTk):
    def __init__(self):
        super().__init__()

        self.title("Project")
        self.geometry("600x480")


        rightframe = CTkFrame(self,width=600,height=480, )
        rightframe.pack_propagate(False)
        rightframe.pack(side="right")

        self.label_title= CTkEntry(rightframe,placeholder_text="количество")
        self.label_title.pack(anchor="center",padx = 20,pady=(20,0))

        self.switch=CTkSwitch(rightframe,text="Тактика")
        self.switch.pack(anchor="center",padx=20,pady=10)

        self.switch_1 = CTkSwitch(rightframe, text="Время 2x")
        self.switch_1.pack(anchor="center", padx=20, pady=10)

        self.button = CTkButton(rightframe, text="Играть", command=self.button_click)
        self.button.pack(anchor="center", padx=20, pady=10)

        self.button_1 = CTkButton(rightframe, text="Назад", command=self.button_click)
        self.button_1.pack(anchor="center", padx=20, pady=10)


    def button_click(self):
        if int(self.label_title.get()) < 101:
            count = int(self.label_title.get())
            app = LoginApp1(count)
            app.mainloop()








if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()