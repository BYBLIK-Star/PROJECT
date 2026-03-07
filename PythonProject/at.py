import random
import customtkinter as ctk


class GamePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master

        self.info_label = ctk.CTkLabel(self, text="Игра 100 заключённых")
        self.info_label.pack(pady=10)

        self.result_label = ctk.CTkLabel(self, text="")
        self.result_label.pack(pady=10)

        self.simulate_btn = ctk.CTkButton(
            self,
            text="Запустить игру",
            command=self.simulate_game
        )
        self.simulate_btn.pack(pady=10)

        self.multi_sim_btn = ctk.CTkButton(
            self,
            text="1000 симуляций",
            command=self.simulate_many
        )
        self.multi_sim_btn.pack(pady=10)

        self.back_btn = ctk.CTkButton(
            self,
            text="Назад",
            command=master.show_main
        )
        self.back_btn.pack(pady=20)

    # --- одна игра ---
    def simulate_game(self):

        boxes = list(range(1, 101))
        random.shuffle(boxes)

        success = True

        for prisoner in range(1, 101):

            next_box = prisoner

            for _ in range(50):
                number_inside = boxes[next_box - 1]

                if number_inside == prisoner:
                    break

                next_box = number_inside
            else:
                success = False
                break

        if success:
            self.result_label.configure(text="✅ Все выжили!")
        else:
            self.result_label.configure(text="❌ Кто-то не нашёл свой номер")

    # --- много симуляций ---
    def simulate_many(self):

        wins = 0
        simulations = 1000

        for _ in range(simulations):
            boxes = list(range(1, 101))
            random.shuffle(boxes)

            success = True

            for prisoner in range(1, 101):
                next_box = prisoner

                for _ in range(50):
                    number_inside = boxes[next_box - 1]

                    if number_inside == prisoner:
                        break

                    next_box = number_inside
                else:
                    success = False
                    break

            if success:
                wins += 1

        probability = wins / simulations * 100

        self.result_label.configure(
            text=f"Победы: {wins} из {simulations}\n≈ {probability:.2f}%"
        )