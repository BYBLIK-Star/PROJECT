from customtkinter import *
from random import shuffle


class LoginApp1(CTk):
    def __init__(self, count):
        super().__init__()

        self.title("Project")
        self.geometry("600x480")

        leftframe = CTkFrame(self,width=600,height=480,fg_color="transparent")
        leftframe.pack(side="left",fill="both", expand=True,padx=20,pady=20)


        hide_numbers = []


        for i in range(1, 101):
            hide_numbers.append(i)

        shuffle(hide_numbers)
        print(hide_numbers)

        cnt = 0
        row = 0

        def create_buttons(self):
            for i in range(9):
                btn = ctk.CTkButton(self.grid_frame, text="", width=100, height=100,
                                    font=("Arial", 32, "bold"),
                                    command=lambda i=i: self.make_move(i))
                btn.grid(row=i // 3, column=i % 3, padx=5, pady=5)
                self.buttons.append(btn)

    def button_click(self,event,column):
        print("dsad",event,column)







if __name__ == "__main__":
    app = LoginApp1()
    app.mainloop()