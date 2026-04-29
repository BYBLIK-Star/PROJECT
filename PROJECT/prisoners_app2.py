import math
import random
from pathlib import Path
from typing import Dict, List, Optional

import customtkinter as ctk

from game_logic import (
    DEFAULT_CELLS,
    generate_boxes,
    theoretical_optimal_success_rate,
    theoretical_random_success_rate,
)
from stats_store import StatsStore

STATS_DB = Path(__file__).with_name("prisoners_stats.db")
LEGACY_STATS_FILE = Path(__file__).with_name("prisoners_stats.json")

BG_COLOR = "#2f6a56"
SURFACE_COLOR = "#3e836a"
SURFACE_DARK = "#367764"
PANEL_COLOR = "#4c8573"
BORDER_COLOR = "#23f2e0"
TEXT_PRIMARY = "#f5f8f6"
TEXT_MUTED = "#d8e8dd"
TEXT_DIM = "#b7cdc1"
GREEN = "#06a20c"
GREEN_HOVER = "#058a0a"
BLUE = "#18588c"
BLUE_HOVER = "#14486f"
RED = "#f22408"
RED_HOVER = "#cd1d06"
ACCENT = "#1ea0ff"
CARD_NEUTRAL = "#32594c"
CELL_COLOR = "#85988f"
CELL_HOVER = "#92a39b"
SUCCESS_COLOR = "#45aa61"
FAIL_COLOR = "#bf675b"


class PrisonersApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("100 заключенных")
        self.geometry("1100x760")
        self.minsize(960, 700)
        self.configure(fg_color=BG_COLOR)

        self.container = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

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
        self.stats_kpi_labels: Dict[str, ctk.CTkLabel] = {}
        self.stats_n_cards: Dict[int, Dict[str, ctk.CTkLabel]] = {}
        self.stats_fact_label: Optional[ctk.CTkLabel] = None
        self.stats_store = StatsStore(STATS_DB, legacy_json_path=LEGACY_STATS_FILE)
        self.stats_detail_ns: List[int] = [10, 25]
        self.board_wrap: Optional[ctk.CTkScrollableFrame] = None
        self.round_summary: Optional[ctk.CTkFrame] = None
        self.game_header: Optional[ctk.CTkFrame] = None
        self.game_prisoner_card: Optional[ctk.CTkFrame] = None
        self.game_rules_card: Optional[ctk.CTkFrame] = None
        self.game_status_value: Optional[ctk.CTkLabel] = None
        self.game_attempts_value: Optional[ctk.CTkLabel] = None
        self.prisoner_badge_label: Optional[ctk.CTkLabel] = None
        self.cell_buttons: List[ctk.CTkButton] = []
        self.setup_summary_label: Optional[ctk.CTkLabel] = None
        self.quick_pick_buttons: List[ctk.CTkButton] = []
        self.mode_buttons: Dict[str, ctk.CTkButton] = {}
        self.game_mode = "manual"
        self.auto_job: Optional[str] = None
        self.auto_sequence: List[int] = []
        self.auto_step_index = 0

        self.show_main_menu()

    def clear_container(self) -> None:
        self._cancel_auto_job()
        for child in self.container.winfo_children():
            child.destroy()
        self.board_wrap = None
        self.round_summary = None
        self.game_header = None
        self.game_prisoner_card = None
        self.game_rules_card = None
        self.game_status_value = None
        self.game_attempts_value = None
        self.prisoner_badge_label = None

    def _record_completed_game(self, won: bool, total_prisoners: int, saved_prisoners: int) -> None:
        try:
            self.stats_store.record_game(
                won=won,
                total_prisoners=total_prisoners,
                saved_prisoners=saved_prisoners,
            )
            self.stats_store.save()
        except Exception:
            self._set_status("Не удалось сохранить статистику на диск.", "#ffb0b0")

    def _make_panel(
        self,
        parent,
        *,
        fg_color: str = SURFACE_COLOR,
        corner_radius: int = 16,
        border_width: int = 1,
        border_color: str = BORDER_COLOR,
    ) -> ctk.CTkFrame:
        return ctk.CTkFrame(
            parent,
            fg_color=fg_color,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
        )

    def _make_button(
        self,
        parent,
        text: str,
        *,
        command,
        fg_color: str,
        hover_color: str,
        width: int,
        height: int,
        font_size: int,
        bold: bool = False,
        corner_radius: int = 12,
        text_color: str = TEXT_PRIMARY,
    ) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            width=width,
            height=height,
            corner_radius=corner_radius,
            font=ctk.CTkFont(size=font_size, weight="bold" if bold else "normal"),
        )

    def show_main_menu(self) -> None:
        self.clear_container()

        card = self._make_panel(self.container, fg_color=SURFACE_COLOR, corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(padx=68, pady=36)

        ctk.CTkLabel(
            content,
            text="100 заключенных",
            font=ctk.CTkFont(size=28, weight="normal"),
            text_color=TEXT_PRIMARY,
        ).pack(pady=(0, 18))

        self._make_button(
            content,
            "Играть",
            command=self.show_game_setup,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            width=315,
            height=68,
            font_size=26,
        ).pack(pady=6)

        self._make_button(
            content,
            "Статистика",
            command=self.show_stats_page,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            width=315,
            height=68,
            font_size=24,
        ).pack(pady=6)

        self._make_button(
            content,
            "Выйти",
            command=self.destroy,
            fg_color=RED,
            hover_color=RED_HOVER,
            width=315,
            height=68,
            font_size=24,
        ).pack(pady=6)

        ctk.CTkLabel(
            content,
            text="Классическая логическая задача\nНайдите свой номер среди 100 ящиков",
            font=ctk.CTkFont(size=16),
            text_color=TEXT_MUTED,
            justify="center",
        ).pack(pady=(18, 0))

    def show_game_setup(self) -> None:
        self.clear_container()

        panel = self._make_panel(self.container, fg_color=SURFACE_COLOR, corner_radius=20)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        body = ctk.CTkFrame(panel, fg_color="transparent")
        body.pack(padx=34, pady=28)

        ctk.CTkLabel(
            body,
            text="Настройка игры",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(pady=(0, 24))

        title_row = ctk.CTkFrame(body, fg_color="transparent")
        title_row.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            title_row,
            text="Количество заключенных:",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0c1110",
        ).pack(anchor="w")

        input_card = self._make_panel(body, fg_color=SURFACE_DARK, corner_radius=10, border_width=0)
        input_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            input_card,
            text="Введите число (от 2 до 1000):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(12, 6))

        self.cells_entry = ctk.CTkEntry(
            input_card,
            width=220,
            height=44,
            justify="center",
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color="#547d72",
            border_color="#91a89c",
            text_color=TEXT_PRIMARY,
        )
        self.cells_entry.pack(pady=(0, 18))
        self.cells_entry.insert(0, str(DEFAULT_CELLS))
        self.cells_entry.bind("<KeyRelease>", lambda _event: self._refresh_setup_preview())

        summary_card = self._make_panel(body, fg_color=SURFACE_DARK, corner_radius=10, border_width=0)
        summary_card.pack(fill="x", pady=(0, 18))

        self.setup_summary_label = ctk.CTkLabel(
            summary_card,
            text="100\nПопыток на каждого: 50",
            font=ctk.CTkFont(size=19),
            text_color=TEXT_MUTED,
            justify="center",
        )
        self.setup_summary_label.pack(pady=14)

        ctk.CTkLabel(
            body,
            text="Быстрый выбор:",
            font=ctk.CTkFont(size=16),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 10))

        quick_grid = ctk.CTkFrame(body, fg_color="transparent")
        quick_grid.pack(fill="x", pady=(0, 18))
        quick_values = [10, 25, 50, 100, 150, 200]
        self.quick_pick_buttons = []
        for idx, value in enumerate(quick_values):
            row = idx // 3
            col = idx % 3
            btn = self._make_button(
                quick_grid,
                str(value),
                command=lambda v=value: self._set_quick_pick(v),
                fg_color="#66887c",
                hover_color="#739488",
                width=110,
                height=34,
                font_size=17,
                corner_radius=6,
            )
            btn.grid(row=row, column=col, padx=8, pady=6)
            self.quick_pick_buttons.append(btn)

        self._make_button(
            body,
            "Начать игру",
            command=self.start_interactive_game,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            width=315,
            height=66,
            font_size=24,
            bold=True,
        ).pack(pady=(2, 10))

        self._make_button(
            body,
            "Назад",
            command=self.show_main_menu,
            fg_color=RED,
            hover_color=RED_HOVER,
            width=315,
            height=40,
            font_size=18,
        ).pack()

        self.status_label = ctk.CTkLabel(
            self.container,
            text="",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#ffb0b0",
        )
        self.status_label.pack(side="bottom", pady=(0, 10))
        self.counter_label = ctk.CTkLabel(self.container, text="")
        self._refresh_setup_preview()

    def show_stats_page(self) -> None:
        self.clear_container()

        page = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent",
            scrollbar_button_color="#447b69",
            scrollbar_button_hover_color="#508774",
        )
        page.pack(fill="both", expand=True)

        header = self._make_panel(page, fg_color=SURFACE_COLOR, corner_radius=14)
        header.pack(fill="x", padx=110, pady=(26, 22))

        top_row = ctk.CTkFrame(header, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(10, 0))

        self._make_button(
            top_row,
            "<-  Назад",
            command=self.show_main_menu,
            fg_color=RED,
            hover_color=RED_HOVER,
            width=96,
            height=28,
            font_size=12,
            corner_radius=8,
        ).pack(side="left")

        self._make_button(
            top_row,
            "Экспорт данных",
            command=lambda: self._set_status("Экспорт данных пока не реализован.", TEXT_MUTED),
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            width=132,
            height=28,
            font_size=12,
            corner_radius=8,
        ).pack(side="right")

        ctk.CTkLabel(
            header,
            text="Статистика",
            font=ctk.CTkFont(size=38, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=54, pady=(0, 6))

        ctk.CTkLabel(
            header,
            text="Общая статистика",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=64, pady=(0, 14))

        self.status_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_MUTED,
        )
        self.status_label.pack(anchor="w", padx=64, pady=(0, 8))

        kpi_row = ctk.CTkFrame(header, fg_color="transparent")
        kpi_row.pack(fill="x", padx=52, pady=(0, 22))
        kpi_row.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.stats_kpi_labels = {}

        def _kpi_card(col: int, title: str, key: str, color: str) -> None:
            card = self._make_panel(kpi_row, fg_color=color, corner_radius=10, border_width=1, border_color=color)
            card.grid(row=0, column=col, padx=5, sticky="nsew")
            value_label = ctk.CTkLabel(
                card,
                text="0",
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=TEXT_PRIMARY,
            )
            value_label.pack(pady=(14, 2))
            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=14),
                text_color=TEXT_MUTED,
            ).pack(pady=(0, 12))
            self.stats_kpi_labels[key] = value_label

        _kpi_card(0, "Всего игр", "games", "#2b584b")
        _kpi_card(1, "Процент побед", "win_rate", "#396856")
        _kpi_card(2, "Побед", "wins", "#46a85a")
        _kpi_card(3, "Поражений", "losses", "#8b5b52")

        ctk.CTkLabel(
            page,
            text="Статистика по количеству заключенных",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=160, pady=(12, 18))

        controls = ctk.CTkFrame(page, fg_color="transparent")
        controls.pack(anchor="w", padx=160, pady=(0, 14))

        self.stats_cells_entry = ctk.CTkEntry(
            controls,
            width=120,
            height=34,
            font=ctk.CTkFont(size=16),
            fg_color="#547d72",
            border_color="#91a89c",
            text_color=TEXT_PRIMARY,
        )
        self.stats_cells_entry.pack(side="left", padx=(0, 8))
        self.stats_cells_entry.insert(0, str(DEFAULT_CELLS))

        self._make_button(
            controls,
            "Обновить",
            command=self.run_stats,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            width=120,
            height=34,
            font_size=14,
            corner_radius=8,
        ).pack(side="left")

        details_row = ctk.CTkFrame(page, fg_color="transparent")
        details_row.pack(fill="x", padx=135, pady=(0, 20))
        details_row.grid_columnconfigure((0, 1), weight=1)

        self.stats_n_cards = {}

        def _stat_chip(parent, key: str, title: str, color: str) -> ctk.CTkLabel:
            chip = self._make_panel(parent, fg_color=color, corner_radius=6, border_width=0)
            chip.pack(side="left", padx=7)
            value = ctk.CTkLabel(
                chip,
                text="0",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=TEXT_PRIMARY,
            )
            value.pack(padx=18, pady=(6, 0))
            ctk.CTkLabel(
                chip,
                text=title,
                font=ctk.CTkFont(size=9),
                text_color=TEXT_MUTED,
            ).pack(padx=18, pady=(0, 6))
            return value

        def _n_card(col: int, n_value: int, border: str) -> None:
            card = self._make_panel(details_row, fg_color=SURFACE_COLOR, corner_radius=14, border_color=border)
            card.grid(row=0, column=col, padx=14, sticky="nsew")

            head = ctk.CTkFrame(card, fg_color="transparent")
            head.pack(fill="x", padx=14, pady=(10, 8))
            badge = self._make_panel(head, fg_color="#2560ff", corner_radius=10, border_width=0)
            badge.pack(side="left")
            ctk.CTkLabel(
                badge,
                text="P",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=TEXT_PRIMARY,
                width=40,
                height=34,
            ).pack()

            title_wrap = ctk.CTkFrame(head, fg_color="transparent")
            title_wrap.pack(side="left", padx=10)

            title_label = ctk.CTkLabel(
                title_wrap,
                text=f"{n_value} заключенных",
                font=ctk.CTkFont(size=17, weight="bold"),
                text_color=TEXT_PRIMARY,
            )
            title_label.pack(anchor="w")
            attempts_label = ctk.CTkLabel(
                title_wrap,
                text=f"Попыток: {n_value // 2}",
                font=ctk.CTkFont(size=13),
                text_color=TEXT_DIM,
            )
            attempts_label.pack(anchor="w")

            ctk.CTkFrame(card, fg_color="#d8e8dd", height=1).pack(fill="x", padx=12, pady=(0, 10))

            ctk.CTkLabel(
                card,
                text="Игры",
                font=ctk.CTkFont(size=12),
                text_color=TEXT_MUTED,
            ).pack(anchor="w", padx=14)

            games_row = ctk.CTkFrame(card, fg_color="transparent")
            games_row.pack(padx=14, pady=(8, 8))
            games_label = _stat_chip(games_row, "games", "Всего", "#92a59c")
            wins_label = _stat_chip(games_row, "wins", "Побед", "#47a962")
            losses_label = _stat_chip(games_row, "losses", "Поражений", "#8a6257")

            ctk.CTkLabel(
                card,
                text="Заключенные",
                font=ctk.CTkFont(size=12),
                text_color=TEXT_MUTED,
            ).pack(anchor="w", padx=14, pady=(2, 0))

            prisoners_row = ctk.CTkFrame(card, fg_color="transparent")
            prisoners_row.pack(padx=14, pady=(8, 6))
            saved_label = _stat_chip(prisoners_row, "saved", "Нашли", "#47a962")
            lost_label = _stat_chip(prisoners_row, "lost", "Проиграли", "#8a6257")

            win_rate_label = ctk.CTkLabel(
                card,
                text="0.0% успешность",
                font=ctk.CTkFont(size=15),
                text_color=TEXT_PRIMARY,
            )
            win_rate_label.pack(pady=(0, 14))

            self.stats_n_cards[n_value] = {
                "title": title_label,
                "attempts": attempts_label,
                "games": games_label,
                "wins": wins_label,
                "losses": losses_label,
                "saved": saved_label,
                "lost": lost_label,
                "win_rate": win_rate_label,
            }

        _n_card(0, 10, ACCENT)
        _n_card(1, 25, BORDER_COLOR)

        fact_card = self._make_panel(page, fg_color=SURFACE_COLOR, corner_radius=8)
        fact_card.pack(fill="x", padx=146, pady=(0, 26))
        self.stats_fact_label = ctk.CTkLabel(
            fact_card,
            text="Интересный факт:",
            font=ctk.CTkFont(size=15),
            text_color=TEXT_MUTED,
            justify="left",
            wraplength=760,
        )
        self.stats_fact_label.pack(anchor="w", padx=18, pady=12)

        self.run_stats()

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
            text=f"{n}\nПопыток на каждого: {attempts}",
            text_color="#19ff22" if n >= 2 else TEXT_MUTED,
        )

        for btn in self.quick_pick_buttons:
            try:
                btn_value = int(btn.cget("text"))
            except (TypeError, ValueError):
                continue
            if btn_value == n:
                btn.configure(fg_color=ACCENT, hover_color=ACCENT)
            else:
                btn.configure(fg_color="#66887c", hover_color="#739488")

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
        self.boxes = generate_boxes(self.total_cells)
        self.cell_buttons = []
        self.game_mode = "manual"

        self._show_gameplay_screen()
        self._start_round()

    def _show_gameplay_screen(self) -> None:
        self.clear_container()

        self.game_header = self._make_panel(self.container, fg_color=SURFACE_COLOR, corner_radius=12)
        self.game_header.pack(fill="x", padx=8, pady=(4, 10))

        header_top = ctk.CTkFrame(self.game_header, fg_color="transparent")
        header_top.pack(fill="x", padx=10, pady=(10, 8))

        self._make_button(
            header_top,
            "<-  Назад",
            command=self.show_game_setup,
            fg_color=RED,
            hover_color=RED_HOVER,
            width=88,
            height=26,
            font_size=11,
            corner_radius=8,
        ).pack(side="left")

        right_controls = ctk.CTkFrame(header_top, fg_color="transparent")
        right_controls.pack(side="right")

        self.game_attempts_value = ctk.CTkLabel(
            right_controls,
            text="0 / 0",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_PRIMARY,
            fg_color="#1ab8b0",
            corner_radius=8,
            width=58,
            height=24,
        )
        self.game_attempts_value.pack(side="left", padx=(0, 8))

        self._make_button(
            right_controls,
            "Новая игра",
            command=self.start_interactive_game,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            width=108,
            height=24,
            font_size=11,
            corner_radius=8,
        ).pack(side="left")

        info_row = ctk.CTkFrame(self.game_header, fg_color="transparent")
        info_row.pack(fill="x", padx=12, pady=(0, 6))

        self.status_label = ctk.CTkLabel(
            info_row,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_PRIMARY,
            justify="left",
        )
        self.status_label.pack(anchor="w")

        self.counter_label = ctk.CTkLabel(
            info_row,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
            justify="left",
        )
        self.counter_label.pack(anchor="w", pady=(2, 8))

        mode_row = ctk.CTkFrame(self.game_header, fg_color="transparent")
        mode_row.pack(anchor="e", padx=12, pady=(0, 10))

        self.mode_buttons = {}
        mode_specs = [("manual", "Каждый"), ("cycle", "Цикл"), ("random", "Случайно")]
        for mode_key, label in mode_specs:
            btn = self._make_button(
                mode_row,
                label,
                command=lambda m=mode_key: self._switch_game_mode(m),
                fg_color="#466d7a",
                hover_color="#3d6170",
                width=72,
                height=24,
                font_size=10,
                corner_radius=8,
            )
            btn.pack(side="left", padx=4)
            self.mode_buttons[mode_key] = btn
        self._refresh_mode_buttons()

        self.game_prisoner_card = self._make_panel(self.container, fg_color=PANEL_COLOR, corner_radius=10)
        self.game_prisoner_card.pack(fill="x", padx=8, pady=(0, 10))

        ctk.CTkLabel(
            self.game_prisoner_card,
            text="P",
            font=ctk.CTkFont(size=46, weight="bold"),
            text_color="#ff9933",
            width=120,
            height=80,
            fg_color="#304d5d",
            corner_radius=10,
        ).pack(pady=(18, 8))

        self.prisoner_badge_label = ctk.CTkLabel(
            self.game_prisoner_card,
            text="Заключенный #1",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_PRIMARY,
            fg_color="#4b6075",
            corner_radius=10,
            width=150,
            height=24,
        )
        self.prisoner_badge_label.pack(pady=(0, 12))

        self.game_rules_card = self._make_panel(self.container, fg_color=SURFACE_COLOR, corner_radius=12)

    def _refresh_mode_buttons(self) -> None:
        for mode, btn in self.mode_buttons.items():
            if mode == self.game_mode:
                btn.configure(fg_color="#2e6fe9", hover_color="#2e6fe9")
            else:
                btn.configure(fg_color="#466d7a", hover_color="#3d6170")

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
            f"Заключенный: {self.prisoner_number} / {self.total_cells}\n"
            f"Попыток осталось: {self.max_open}",
            TEXT_PRIMARY,
        )
        self._update_counter()
        if self.board_wrap is None or len(self.cell_buttons) != self.total_cells:
            self.render_game_board()
        else:
            self._reset_board_buttons()
        if self.prisoner_badge_label:
            self.prisoner_badge_label.configure(text=f"Заключенный #{self.prisoner_number}")
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
                    f"Открыто: {self.opened_count}/{self.max_open} | "
                    f"Успехи: {self.successful_rounds} | Поражения: {self.failed_rounds}"
                )
            )
        if self.game_attempts_value:
            self.game_attempts_value.configure(text=f"{self.opened_count:02d}")

    def render_game_board(self) -> None:
        if self.board_wrap is not None:
            self.board_wrap.destroy()
            self.board_wrap = None
        if self.round_summary is not None:
            self.round_summary.destroy()
            self.round_summary = None
        if self.game_rules_card is not None:
            self.game_rules_card.pack_forget()

        board_panel = self._make_panel(self.container, fg_color=SURFACE_COLOR, corner_radius=12)
        board_panel.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        self.board_wrap = ctk.CTkScrollableFrame(
            board_panel,
            fg_color="transparent",
            scrollbar_button_color="#447b69",
            scrollbar_button_hover_color="#508774",
        )
        self.board_wrap.pack(fill="both", expand=True, padx=18, pady=18)
        self.cell_buttons = []

        cols = max(6, min(10, int(math.sqrt(self.total_cells))))
        btn_width = 60 if self.total_cells <= 100 else 52
        btn_height = 44 if self.total_cells <= 100 else 40

        for idx in range(self.total_cells):
            row = idx // cols
            col = idx % cols
            btn = ctk.CTkButton(
                self.board_wrap,
                text=str(idx + 1),
                width=btn_width,
                height=btn_height,
                corner_radius=6,
                fg_color=CELL_COLOR,
                hover_color=CELL_HOVER,
                text_color=TEXT_PRIMARY,
                font=ctk.CTkFont(size=16, weight="bold"),
            )
            btn.configure(command=lambda i=idx, b=btn: self.open_cell(i, b))
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.cell_buttons.append(btn)

        if self.game_rules_card is not None:
            self.game_rules_card.pack(fill="x", padx=8, pady=(0, 2))
            ctk.CTkLabel(
                self.game_rules_card,
                text=(
                    "Правила игры:\n\n"
                    "  * Каждый заключенный должен найти свой номер в 100 ящиках\n"
                    "  * У каждого заключенного есть 50 попыток\n"
                    "  * Если хотя бы один заключенный не найдет свой номер - все проигрывают\n"
                    "  * Стратегия \"ЦИКЛ\" дает около 31% шанса на победу для всех заключенных"
                ),
                font=ctk.CTkFont(size=15),
                text_color=TEXT_PRIMARY,
                justify="left",
            ).pack(anchor="w", padx=18, pady=14)

    def _reset_board_buttons(self) -> None:
        for idx, btn in enumerate(self.cell_buttons):
            btn.configure(
                text=str(idx + 1),
                state="normal",
                fg_color=CELL_COLOR,
                hover_color=CELL_HOVER,
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
            button.configure(fg_color=SUCCESS_COLOR, hover_color=SUCCESS_COLOR)
            self.successful_rounds += 1
            self._finish_round(True)
            return

        button.configure(fg_color=FAIL_COLOR, hover_color=FAIL_COLOR)

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
                f"Заключенный: {self.prisoner_number} / {self.total_cells}\n"
                "Номер найден. Переход к следующему.",
                "#b2ffd1",
            )
            self.after(1, self._next_prisoner_or_finish_game)
        else:
            self._record_completed_game(
                won=False,
                total_prisoners=self.total_cells,
                saved_prisoners=self.successful_rounds,
            )
            self._set_status(
                f"Заключенный: {self.prisoner_number} / {self.total_cells}\n"
                "Номер не найден. Игра завершена.",
                "#ffd1d1",
            )
            self._show_game_over_summary()

    def _next_prisoner_or_finish_game(self) -> None:
        self.prisoner_number += 1

        if self.prisoner_number <= self.total_cells:
            self._start_round()
            return

        if self.board_wrap is not None:
            self.board_wrap.master.destroy()
            self.board_wrap = None
        if self.round_summary is not None:
            self.round_summary.destroy()
            self.round_summary = None

        total = self.total_cells
        self._record_completed_game(
            won=True,
            total_prisoners=self.total_cells,
            saved_prisoners=self.successful_rounds,
        )
        self._set_status(
            f"Заключенный: {total} / {total}\n"
            f"Серия завершена. Успехов: {self.successful_rounds}, поражений: {self.failed_rounds}.",
            TEXT_PRIMARY,
        )
        self._update_counter()

        self.round_summary = self._make_panel(self.container, fg_color=SURFACE_COLOR, corner_radius=12)
        self.round_summary.pack(fill="x", padx=8, pady=(8, 10))

        ctk.CTkLabel(
            self.round_summary,
            text="Серия заключенных пройдена",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(pady=(14, 8))

        ctk.CTkLabel(
            self.round_summary,
            text=f"Успешно нашли номер: {self.successful_rounds}\nНе нашли номер: {self.failed_rounds}",
            font=ctk.CTkFont(size=15),
            text_color=TEXT_MUTED,
            justify="center",
        ).pack(pady=(0, 10))

        self._make_button(
            self.round_summary,
            "Новая игра",
            command=self.start_interactive_game,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            width=180,
            height=40,
            font_size=15,
            bold=True,
        ).pack(pady=(0, 14))

    def _show_game_over_summary(self) -> None:
        self._cancel_auto_job()
        if self.board_wrap is not None:
            self.board_wrap.master.destroy()
            self.board_wrap = None
        if self.round_summary is not None:
            self.round_summary.destroy()
            self.round_summary = None

        self._update_counter()

        self.round_summary = self._make_panel(self.container, fg_color=SURFACE_COLOR, corner_radius=12)
        self.round_summary.pack(fill="x", padx=8, pady=(8, 10))

        ctk.CTkLabel(
            self.round_summary,
            text=f"Игра завершена: номер не найден за {self.max_open} попыток",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffd1d1",
        ).pack(pady=(14, 8))

        ctk.CTkLabel(
            self.round_summary,
            text=(
                f"Успешно пройдено заключенных: {self.successful_rounds}\n"
                f"Провал на заключенном: #{self.prisoner_number}"
            ),
            font=ctk.CTkFont(size=15),
            text_color=TEXT_MUTED,
            justify="center",
        ).pack(pady=(0, 10))

        self._make_button(
            self.round_summary,
            "Новая игра",
            command=self.start_interactive_game,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            width=180,
            height=40,
            font_size=15,
            bold=True,
        ).pack(pady=(0, 14))

    def run_stats(self) -> None:
        if not self.stats_cells_entry:
            return

        n = self._parse_positive_int(self.stats_cells_entry.get())
        if n is None:
            self._set_status("Количество заключенных должно быть целым числом больше 1.", "#ffb0b0")
            return

        self.stats_detail_ns = [n, 100]
        self._set_status("Показаны сохраненные результаты игр.", TEXT_MUTED)
        total_summary = self.stats_store.total_summary()

        if self.stats_kpi_labels:
            self.stats_kpi_labels["games"].configure(text=str(total_summary["games"]))
            self.stats_kpi_labels["win_rate"].configure(text=f"{total_summary['win_rate']:.1f}%")
            self.stats_kpi_labels["wins"].configure(text=str(total_summary["wins"]))
            self.stats_kpi_labels["losses"].configure(text=str(total_summary["losses"]))

        card_keys = list(self.stats_n_cards.keys())
        for idx, card_n in enumerate(card_keys):
            labels = self.stats_n_cards[card_n]
            n_value = self.stats_detail_ns[idx] if idx < len(self.stats_detail_ns) else card_n
            n_summary = self.stats_store.summary_for_n(n_value)

            labels["title"].configure(text=f"{n_value} заключенных")
            labels["attempts"].configure(text=f"Попыток: {n_value // 2}")
            labels["games"].configure(text=str(n_summary["games"]))
            labels["wins"].configure(text=str(n_summary["wins"]))
            labels["losses"].configure(text=str(n_summary["losses"]))
            labels["saved"].configure(text=str(n_summary["saved_prisoners"]))
            labels["lost"].configure(text=str(n_summary["lost_prisoners"]))
            labels["win_rate"].configure(text=f"{n_summary['win_rate']:.1f}% успешность")

        if self.stats_fact_label:
            theory_100 = theoretical_optimal_success_rate(100)
            theory_100_random = theoretical_random_success_rate(100)
            self.stats_fact_label.configure(
                text=(
                    "Интересный факт:\n"
                    "При использовании стратегии \"следования по циклу\" вероятность успеха всех 100 "
                    f"заключенных составляет около {theory_100:.0f}%, что намного выше случайных "
                    f"{theory_100_random:.30f}%."
                )
            )


def main() -> None:
    app = PrisonersApp()
    app.mainloop()


if __name__ == "__main__":
    main()
