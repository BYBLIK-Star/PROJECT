import math
import random
from typing import Dict, List, Optional

import customtkinter as ctk

DEFAULT_CELLS = 100
DEFAULT_RUNS = 1000
INTERACTIVE_MAX_ATTEMPTS = 5


# ------------------------------
# Simulation core
# ------------------------------

def generate_boxes(total_prisoners: int) -> List[int]:
    boxes = list(range(1, total_prisoners + 1))
    random.shuffle(boxes)
    return boxes


def simulate_prisoner(
    prisoner_number: int,
    boxes: List[int],
    strategy: str,
    max_boxes_to_open: int,
) -> bool:
    total_prisoners = len(boxes)

    if strategy == "random":
        opened = random.sample(range(total_prisoners), k=max_boxes_to_open)
        return any(boxes[idx] == prisoner_number for idx in opened)

    if strategy == "optimal":
        current_index = prisoner_number - 1
        for _ in range(max_boxes_to_open):
            found = boxes[current_index]
            if found == prisoner_number:
                return True
            current_index = found - 1
        return False

    raise ValueError("Unknown strategy")


def simulate_game(strategy: str, total_prisoners: int) -> bool:
    boxes = generate_boxes(total_prisoners)
    max_open = total_prisoners // 2

    for prisoner_number in range(1, total_prisoners + 1):
        if not simulate_prisoner(prisoner_number, boxes, strategy, max_open):
            return False
    return True


def run_mass_simulation(strategy: str, runs: int, total_prisoners: int) -> Dict[str, float]:
    success = 0
    for _ in range(runs):
        if simulate_game(strategy=strategy, total_prisoners=total_prisoners):
            success += 1

    failed = runs - success
    rate = (success / runs) * 100 if runs > 0 else 0.0
    return {
        "runs": runs,
        "successful_attempts": success,
        "failed_attempts": failed,
        "win_rate": rate,
    }


# ------------------------------
# App
# ------------------------------

class PrisonersApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("100 заключенных")
        self.geometry("1100x760")
        self.minsize(940, 640)

        self.configure(fg_color="#070f37")

        self.container = ctk.CTkFrame(self, fg_color="#15245f")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # runtime state
        self.total_cells = DEFAULT_CELLS
        self.prisoner_number = 1
        self.max_open = self.total_cells // 2
        self.boxes: List[int] = []
        self.opened_count = 0
        self.game_finished = False

        self.successful_rounds = 0
        self.failed_rounds = 0

        self.cells_entry: Optional[ctk.CTkEntry] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        self.counter_label: Optional[ctk.CTkLabel] = None

        self.stats_cells_entry: Optional[ctk.CTkEntry] = None
        self.stats_runs_entry: Optional[ctk.CTkEntry] = None
        self.stats_output: Optional[ctk.CTkTextbox] = None
        self.board_wrap: Optional[ctk.CTkScrollableFrame] = None
        self.round_summary: Optional[ctk.CTkFrame] = None
        self.cell_buttons: List[ctk.CTkButton] = []
        self.setup_summary_label: Optional[ctk.CTkLabel] = None
        self.quick_pick_buttons: List[ctk.CTkButton] = []
        self.mode_buttons: Dict[str, ctk.CTkButton] = {}
        self.game_mode = "manual"  # manual | cycle | random
        self.auto_job: Optional[str] = None
        self.auto_sequence: List[int] = []
        self.auto_step_index = 0

        self.show_main_menu()

    # ---------- helpers ----------

    def clear_container(self) -> None:
        self._cancel_auto_job()
        for child in self.container.winfo_children():
            child.destroy()
        self.board_wrap = None
        self.round_summary = None

    def title_label(self, parent, text: str) -> None:
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color="#f3f5ff",
        ).pack(pady=(18, 14))

    # ---------- pages ----------

    def show_main_menu(self) -> None:
        self.clear_container()

        card = ctk.CTkFrame(
            self.container,
            width=420,
            fg_color="#3f4f83",
            corner_radius=18,
            border_width=1,
            border_color="#7f8cbd",
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label(card, "100 заключенных")

        ctk.CTkButton(
            card,
            text="Играть",
            width=280,
            height=50,
            corner_radius=12,
            fg_color="#1140ff",
            hover_color="#0f35d8",
            command=self.show_game_setup,
            font=ctk.CTkFont(size=22),
        ).pack(pady=8)

        ctk.CTkButton(
            card,
            text="Статистика",
            width=280,
            height=50,
            corner_radius=12,
            fg_color="#68769e",
            hover_color="#5a678c",
            command=self.show_stats_page,
            font=ctk.CTkFont(size=22),
        ).pack(pady=8)

        ctk.CTkButton(
            card,
            text="Выйти",
            width=280,
            height=50,
            corner_radius=12,
            fg_color="#ff1414",
            hover_color="#d80f0f",
            command=self.destroy,
            font=ctk.CTkFont(size=22),
        ).pack(pady=8)

        ctk.CTkLabel(
            card,
            text="Найдите свой номер максимум за 5 открытий",
            font=ctk.CTkFont(size=14),
            text_color="#d2daf6",
        ).pack(pady=(10, 18))

    def show_game_setup(self) -> None:
        self.clear_container()

        panel = ctk.CTkFrame(
            self.container,
            width=560,
            fg_color="#2d3f77",
            corner_radius=16,
            border_width=1,
            border_color="#6d7cae",
        )
        panel.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label(panel, "Настройка игры")

        self.quick_pick_buttons = []

        form = ctk.CTkFrame(panel, fg_color="transparent")
        form.pack(padx=28, pady=(0, 16), fill="x")

        ctk.CTkLabel(
            form,
            text="Количество заключенных:",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f3f5ff",
        ).pack(anchor="w", pady=(0, 8))

        input_card = ctk.CTkFrame(form, fg_color="#27376f", corner_radius=10)
        input_card.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            input_card,
            text="Введите число (от 2 до 1000):",
            font=ctk.CTkFont(size=13),
            text_color="#cad4ff",
        ).pack(anchor="w", padx=16, pady=(10, 8))

        self.cells_entry = ctk.CTkEntry(
            input_card,
            width=260,
            height=40,
            justify="center",
            font=ctk.CTkFont(size=28, weight="bold"),
            fg_color="#42507d",
            border_color="#7f8cbd",
        )
        self.cells_entry.pack(pady=(0, 14))
        self.cells_entry.insert(0, str(DEFAULT_CELLS))
        self.cells_entry.bind("<KeyRelease>", lambda _event: self._refresh_setup_preview())

        summary_card = ctk.CTkFrame(form, fg_color="#27376f", corner_radius=10)
        summary_card.pack(fill="x", pady=(0, 10))

        self.setup_summary_label = ctk.CTkLabel(
            summary_card,
            text="100\nПопыток на каждого: 50",
            font=ctk.CTkFont(size=18),
            text_color="#dfe6ff",
            justify="center",
        )
        self.setup_summary_label.pack(pady=10)

        ctk.CTkLabel(
            form,
            text="Быстрый выбор:",
            font=ctk.CTkFont(size=15),
            text_color="#d0d8fb",
        ).pack(anchor="w", pady=(2, 8))

        quick_grid = ctk.CTkFrame(form, fg_color="transparent")
        quick_grid.pack(fill="x", pady=(0, 14))
        quick_values = [10, 25, 50, 100, 150, 200]
        for idx, value in enumerate(quick_values):
            row = idx // 3
            col = idx % 3
            btn = ctk.CTkButton(
                quick_grid,
                text=str(value),
                width=112,
                height=38,
                corner_radius=8,
                font=ctk.CTkFont(size=16),
                fg_color="#5a668d",
                hover_color="#66749f",
                command=lambda v=value: self._set_quick_pick(v),
            )
            btn.grid(row=row, column=col, padx=6, pady=5)
            self.quick_pick_buttons.append(btn)

        btns = ctk.CTkFrame(panel, fg_color="transparent")
        btns.pack(pady=(0, 20))

        ctk.CTkButton(
            btns,
            text="▷  Начать игру",
            width=360,
            height=58,
            font=ctk.CTkFont(size=34, weight="bold"),
            fg_color="#0cff39",
            hover_color="#00de2f",
            text_color="#ffffff",
            command=self.start_interactive_game,
        ).pack(pady=(0, 10))

        ctk.CTkButton(
            btns,
            text="Назад",
            width=360,
            height=46,
            font=ctk.CTkFont(size=18),
            fg_color="#5a668d",
            hover_color="#66749f",
            command=self.show_main_menu,
        ).pack()

        self.status_label = ctk.CTkLabel(
            self.container,
            text="",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#ffb0b0",
        )
        self.status_label.pack(side="bottom", pady=(0, 14))
        self.counter_label = ctk.CTkLabel(self.container, text="")
        self._refresh_setup_preview()

    def show_stats_page(self) -> None:
        self.clear_container()

        panel = ctk.CTkFrame(self.container, fg_color="#2d3f77", corner_radius=16)
        panel.pack(fill="both", expand=True, padx=30, pady=24)

        self.title_label(panel, "Массовая симуляция")

        controls = ctk.CTkFrame(panel, fg_color="transparent")
        controls.pack(padx=20, pady=(0, 10), fill="x")

        ctk.CTkLabel(controls, text="Количество ячеек (N):", font=ctk.CTkFont(size=17)).grid(
            row=0, column=0, padx=8, pady=6, sticky="w"
        )
        self.stats_cells_entry = ctk.CTkEntry(controls, width=150, font=ctk.CTkFont(size=17))
        self.stats_cells_entry.grid(row=0, column=1, padx=8, pady=6, sticky="w")
        self.stats_cells_entry.insert(0, str(DEFAULT_CELLS))

        ctk.CTkLabel(controls, text="Количество прогонов:", font=ctk.CTkFont(size=17)).grid(
            row=1, column=0, padx=8, pady=6, sticky="w"
        )
        self.stats_runs_entry = ctk.CTkEntry(controls, width=150, font=ctk.CTkFont(size=17))
        self.stats_runs_entry.grid(row=1, column=1, padx=8, pady=6, sticky="w")
        self.stats_runs_entry.insert(0, str(DEFAULT_RUNS))

        btns = ctk.CTkFrame(panel, fg_color="transparent")
        btns.pack(pady=(6, 12))

        ctk.CTkButton(
            btns,
            text="Запустить статистику",
            width=240,
            height=46,
            font=ctk.CTkFont(size=17, weight="bold"),
            fg_color="#1140ff",
            hover_color="#0f35d8",
            command=self.run_stats,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btns,
            text="Назад",
            width=180,
            height=46,
            font=ctk.CTkFont(size=17),
            fg_color="#68769e",
            hover_color="#5a678c",
            command=self.show_main_menu,
        ).pack(side="left", padx=8)

        self.stats_output = ctk.CTkTextbox(panel, height=340, font=("Consolas", 15))
        self.stats_output.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.stats_output.insert("1.0", "Нажмите 'Запустить статистику'.")
        self.stats_output.configure(state="disabled")

    # ---------- actions ----------

    def _parse_positive_int(self, text: str) -> Optional[int]:
        value = text.strip()
        if not value.isdigit():
            return None
        number = int(value)
        if number <= 1:
            return None
        return number

    def _refresh_setup_preview(self) -> None:
        if not self.cells_entry or not self.setup_summary_label:
            return

        value = self.cells_entry.get().strip()
        n = int(value) if value.isdigit() else 0
        attempts = n // 2 if n >= 2 else 0
        self.setup_summary_label.configure(
            text=f"{n}\nПопыток на каждого: {attempts}"
        )

        for btn in self.quick_pick_buttons:
            try:
                btn_value = int(btn.cget("text"))
            except (TypeError, ValueError):
                continue
            if btn_value == n:
                btn.configure(fg_color="#0f5dff", hover_color="#0f5dff")
            else:
                btn.configure(fg_color="#5a668d", hover_color="#66749f")

    def _set_quick_pick(self, value: int) -> None:
        if not self.cells_entry:
            return
        self.cells_entry.delete(0, "end")
        self.cells_entry.insert(0, str(value))
        self._refresh_setup_preview()

    def start_interactive_game(self) -> None:
        if self.cells_entry and self.cells_entry.winfo_exists():
            n = self._parse_positive_int(self.cells_entry.get())
            if n is None:
                self._set_status("Введите корректное N (от 2 до 1000).", "#ffb0b0")
                return
            if n > 1000:
                self._set_status("Максимальное N: 1000.", "#ffb0b0")
                return
        else:
            n = self.total_cells

        self.total_cells = n
        self.max_open = self.total_cells // 2

        self.prisoner_number = 1
        self.successful_rounds = 0
        self.failed_rounds = 0
        # В классической задаче расклад коробок фиксирован для всей серии заключенных.
        self.boxes = generate_boxes(self.total_cells)
        self.cell_buttons = []
        self.game_mode = "manual"

        self._show_gameplay_screen()
        self._start_round()

    def _show_gameplay_screen(self) -> None:
        self.clear_container()

        top = ctk.CTkFrame(self.container, fg_color="#2d3f77", corner_radius=14)
        top.pack(fill="x", padx=24, pady=(20, 10))

        controls = ctk.CTkFrame(top, fg_color="transparent")
        controls.pack(pady=(12, 6))

        self.mode_buttons = {}
        mode_specs = [
            ("manual", "Каждый"),
            ("cycle", "Цикл"),
            ("random", "Случайно"),
        ]
        for mode_key, label in mode_specs:
            btn = ctk.CTkButton(
                controls,
                text=label,
                width=140,
                height=38,
                corner_radius=10,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#5a668d",
                hover_color="#66749f",
                command=lambda m=mode_key: self._switch_game_mode(m),
            )
            btn.pack(side="left", padx=6)
            self.mode_buttons[mode_key] = btn
        self._refresh_mode_buttons()

        self.status_label = ctk.CTkLabel(
            top,
            text="",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f5f7ff",
        )
        self.status_label.pack(pady=(12, 6), padx=10)

        self.counter_label = ctk.CTkLabel(
            top,
            text="",
            font=ctk.CTkFont(size=15),
            text_color="#d8def9",
        )
        self.counter_label.pack(pady=(0, 12), padx=10)

    def _refresh_mode_buttons(self) -> None:
        for mode, btn in self.mode_buttons.items():
            if mode == self.game_mode:
                btn.configure(fg_color="#0f5dff", hover_color="#0f5dff")
            else:
                btn.configure(fg_color="#5a668d", hover_color="#66749f")

    def _switch_game_mode(self, mode: str) -> None:
        if mode not in {"manual", "cycle", "random"}:
            return
        self.game_mode = mode
        self._refresh_mode_buttons()
        if self.board_wrap is not None and not self.game_finished:
            self._start_round()

    def _cancel_auto_job(self) -> None:
        if self.auto_job is not None:
            try:
                self.after_cancel(self.auto_job)
            except Exception:
                pass
            self.auto_job = None

    def _prepare_auto_sequence(self) -> None:
        self.auto_step_index = 0
        if self.game_mode == "cycle":
            self.auto_sequence = []
            current_idx = self.prisoner_number - 1
            for _ in range(self.max_open):
                self.auto_sequence.append(current_idx)
                found = self.boxes[current_idx]
                if found == self.prisoner_number:
                    break
                current_idx = found - 1
            return

        if self.game_mode == "random":
            self.auto_sequence = random.sample(range(self.total_cells), k=self.max_open)
            return

        self.auto_sequence = []

    def _schedule_auto_step(self) -> None:
        self._cancel_auto_job()
        if self.game_mode not in {"cycle", "random"}:
            return
        self.auto_job = self.after(25, self._auto_step)

    def _auto_step(self) -> None:
        self.auto_job = None
        if self.game_finished or self.game_mode not in {"cycle", "random"}:
            return
        if self.auto_step_index >= len(self.auto_sequence):
            return

        idx = self.auto_sequence[self.auto_step_index]
        self.auto_step_index += 1
        if 0 <= idx < len(self.cell_buttons):
            self.open_cell(idx, self.cell_buttons[idx], triggered_by_auto=True)
        if not self.game_finished:
            self._schedule_auto_step()

    def _start_round(self) -> None:
        self._cancel_auto_job()
        self.opened_count = 0
        self.game_finished = False

        self._set_status(
            f"Заключенный #{self.prisoner_number}: найдите число {self.prisoner_number} "
            f"за максимум {self.max_open} открытий.",
            "#f5f7ff",
        )
        self._update_counter()
        if self.board_wrap is None or len(self.cell_buttons) != self.total_cells:
            self.render_game_board()
        else:
            self._reset_board_buttons()
        if self.game_mode in {"cycle", "random"}:
            self._prepare_auto_sequence()
            self._schedule_auto_step()

    def _set_status(self, text: str, color: str) -> None:
        if self.status_label:
            self.status_label.configure(text=text, text_color=color)

    def _update_counter(self) -> None:
        if self.counter_label:
            self.counter_label.configure(
                text=(
                    f"Заключенный: {self.prisoner_number}/{self.total_cells} | "
                    f"Открыто: {self.opened_count}/{self.max_open} | "
                    f"Успехи: {self.successful_rounds} | Провалы: {self.failed_rounds}"
                )
            )

    def render_game_board(self) -> None:
        if self.board_wrap is not None:
            self.board_wrap.destroy()
            self.board_wrap = None
        if self.round_summary is not None:
            self.round_summary.destroy()
            self.round_summary = None

        self.board_wrap = ctk.CTkScrollableFrame(
            self.container,
            fg_color="#1b2c63",
            corner_radius=14,
            height=360,
        )
        self.board_wrap.pack(fill="both", expand=True, padx=22, pady=(2, 18))
        self.cell_buttons = []

        cols = max(6, min(14, int(math.sqrt(self.total_cells)) + 2))

        for idx in range(self.total_cells):
            row = idx // cols
            col = idx % cols
            btn = ctk.CTkButton(
                self.board_wrap,
                text=str(idx + 1),
                width=70,
                height=48,
                corner_radius=10,
                fg_color="#3250a3",
                hover_color="#3f61be",
                font=ctk.CTkFont(size=16, weight="bold"),
            )
            btn.configure(command=lambda i=idx, b=btn: self.open_cell(i, b))
            btn.grid(row=row, column=col, padx=6, pady=6)
            self.cell_buttons.append(btn)

    def _reset_board_buttons(self) -> None:
        for idx, btn in enumerate(self.cell_buttons):
            btn.configure(
                text=str(idx + 1),
                state="normal",
                fg_color="#3250a3",
                hover_color="#3f61be",
            )

    def open_cell(self, idx: int, button: ctk.CTkButton, triggered_by_auto: bool = False) -> None:
        if self.game_finished:
            return
        if self.game_mode in {"cycle", "random"} and not triggered_by_auto:
            return
        if str(button.cget("state")) == "disabled":
            return

        self.opened_count += 1
        found = self.boxes[idx]
        button.configure(text=str(found), state="disabled")

        if found == self.prisoner_number:
            button.configure(fg_color="#0f9d58", hover_color="#0f9d58")
            self.successful_rounds += 1
            self._finish_round(True)
            return

        button.configure(fg_color="#d93025", hover_color="#d93025")

        if self.opened_count >= self.max_open:
            self.failed_rounds += 1
            self._finish_round(False)
            return

        self._update_counter()

    def _finish_round(self, won: bool) -> None:
        self.game_finished = True
        self._cancel_auto_job()
        self._update_counter()

        if won:
            self._set_status(
                f"Заключенный #{self.prisoner_number}: успех. "
                f"Переход к следующему...",
                "#90f0a8",
            )
            # Переключаемся в следующий тик UI, чтобы новое поле корректно отрисовалось.
            self.after(1, self._next_prisoner_or_finish_game)
        else:
            self._set_status(
                f"Заключенный #{self.prisoner_number}: провал. "
                f"Игра завершена.",
                "#ff9d9d",
            )
            self._show_game_over_summary()

    def _next_prisoner_or_finish_game(self) -> None:
        self.prisoner_number += 1

        if self.prisoner_number <= self.total_cells:
            self._start_round()
            return

        if self.board_wrap is not None:
            self.board_wrap.destroy()
            self.board_wrap = None
        if self.round_summary is not None:
            self.round_summary.destroy()
            self.round_summary = None

        total = self.total_cells
        self._set_status(
            f"Серия завершена. Успехов: {self.successful_rounds}/{total}, "
            f"Провалов: {self.failed_rounds}/{total}.",
            "#f0f4ff",
        )
        self._update_counter()

        self.round_summary = ctk.CTkFrame(self.container, fg_color="#1b2c63", corner_radius=14)
        self.round_summary.pack(fill="x", padx=22, pady=(8, 18))

        ctk.CTkLabel(
            self.round_summary,
            text="Серия заключенных пройдена.",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f3f5ff",
        ).pack(pady=(14, 8))

        ctk.CTkLabel(
            self.round_summary,
            text=(
                f"Успешно нашли номер: {self.successful_rounds}\n"
                f"Не нашли номер: {self.failed_rounds}"
            ),
            font=ctk.CTkFont(size=16),
            text_color="#d6ddff",
            justify="center",
        ).pack(pady=(0, 12))

        ctk.CTkButton(
            self.round_summary,
            text="Запустить серию заново",
            command=self.start_interactive_game,
            width=240,
            height=42,
            fg_color="#1140ff",
            hover_color="#0f35d8",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(0, 14))

    def _show_game_over_summary(self) -> None:
        self._cancel_auto_job()
        if self.board_wrap is not None:
            self.board_wrap.destroy()
            self.board_wrap = None
        if self.round_summary is not None:
            self.round_summary.destroy()
            self.round_summary = None

        self._update_counter()

        self.round_summary = ctk.CTkFrame(self.container, fg_color="#1b2c63", corner_radius=14)
        self.round_summary.pack(fill="x", padx=22, pady=(8, 18))

        ctk.CTkLabel(
            self.round_summary,
            text=f"Игра завершена: не найден номер за {self.max_open} попыток.",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffb0b0",
        ).pack(pady=(14, 8))

        ctk.CTkLabel(
            self.round_summary,
            text=(
                f"Успешно пройдено заключенных: {self.successful_rounds}\n"
                f"Провал на заключенном: #{self.prisoner_number}"
            ),
            font=ctk.CTkFont(size=16),
            text_color="#d6ddff",
            justify="center",
        ).pack(pady=(0, 12))

        ctk.CTkButton(
            self.round_summary,
            text="Начать заново",
            command=self.start_interactive_game,
            width=240,
            height=42,
            fg_color="#1140ff",
            hover_color="#0f35d8",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(0, 14))

    def run_stats(self) -> None:
        if not self.stats_cells_entry or not self.stats_runs_entry or not self.stats_output:
            return

        n = self._parse_positive_int(self.stats_cells_entry.get())
        runs_val = self._parse_positive_int(self.stats_runs_entry.get())

        if n is None:
            self._set_stats_text("Ошибка: количество ячеек должно быть целым числом > 1.")
            return
        if runs_val is None:
            self._set_stats_text("Ошибка: количество прогонов должно быть целым числом > 1.")
            return

        optimal = run_mass_simulation("optimal", runs=runs_val, total_prisoners=n)
        random_stats = run_mass_simulation("random", runs=runs_val, total_prisoners=n)

        report = (
            f"N = {n}, прогонов = {runs_val}\n\n"
            f"Оптимальная стратегия:\n"
            f"  Успешных попыток: {optimal['successful_attempts']}\n"
            f"  Неудачных попыток: {optimal['failed_attempts']}\n"
            f"  Процент побед: {optimal['win_rate']:.2f}%\n\n"
            f"Случайная стратегия:\n"
            f"  Успешных попыток: {random_stats['successful_attempts']}\n"
            f"  Неудачных попыток: {random_stats['failed_attempts']}\n"
            f"  Процент побед: {random_stats['win_rate']:.2f}%"
        )

        self._set_stats_text(report)

    def _set_stats_text(self, text: str) -> None:
        if not self.stats_output:
            return
        self.stats_output.configure(state="normal")
        self.stats_output.delete("1.0", "end")
        self.stats_output.insert("1.0", text)
        self.stats_output.configure(state="disabled")


def main() -> None:
    app = PrisonersApp()
    app.mainloop()


if __name__ == "__main__":
    main()
