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
        for column in range(count):
            cell= CTkFrame(
                leftframe,
                width=80,
                height=80,
                corner_radius=10,
                border_width=2,
                border_color="gray"
            )
            cell.bind("<Button-1>",lambda column=column: self.button_click(column,cell))
            number = CTkLabel(cell,text=column+1)
            number.pack(side="left",padx=35)
            if cnt==5:
                row+=1
                cnt=0
            cnt+=1
            cell.pack_propagate(0)
            cell.grid(row=row,column=cnt-1)

    def button_click(self,event,column):
        print("dsad",event,column)







if __name__ == "__main__":
    app = LoginApp1()
    app.mainloop()