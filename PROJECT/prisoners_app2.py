import math
import random
import time
import tkinter as tk
from csv import DictWriter
from io import BytesIO
import json
from pathlib import Path
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

import customtkinter as ctk

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import cairosvg
except ImportError:
    cairosvg = None

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
TEXT_FONT_FAMILY = "Jacques Francois Shadow"
NUMBER_FONT_FAMILY = "Abel"
ASSETS_DIR = Path(__file__).with_name("assets") / "icons"
EXPORTS_DIR = Path(__file__).with_name("exports")
EXPORT_HEADERS = [
    "scope",
    "prisoners",
    "games",
    "wins",
    "losses",
    "saved_prisoners",
    "lost_prisoners",
    "win_rate",
]
DEFAULT_STATS_COUNTS = [10, 25, 50, 100]
AUTO_MODES = {"cycle", "random"}
LANGUAGE_OPTIONS = [("en", "English"), ("ru", "Russian"), ("ky", "Kyrgyz")]
TRANSLATIONS = {
    "en": {
        "window_title": "100 prisoners",
        "main_title": "100 prisoners",
        "play": "Play",
        "statistics": "Statistics",
        "exit": "Exit",
        "main_subtitle": "Classic logic puzzle\nFind your number among 100 boxes",
        "game_setup": "Game settings",
        "prisoners_count": "Number of prisoners:",
        "enter_number": "Enter a number (from 2 to 1000):",
        "attempts_per_person": "Attempts per person: {attempts}",
        "quick_selection": "Quick selection:",
        "start_game": "Start game",
        "back": "Back",
        "export_data": "Export data",
        "overall_statistics": "Overall statistics",
        "stats_by_prisoners": "Statistics by number of prisoners",
        "stats_recent_info": "Below is the overall statistics for the two most recent prisoner counts.",
        "total_games": "Total games",
        "win_percentage": "Win percentage",
        "wins": "Wins",
        "losses": "Losses",
        "games": "Games",
        "total": "Total",
        "prisoners": "Prisoners",
        "found": "Found",
        "lost": "Lost",
        "prisoners_n": "{count} prisoners",
        "attempts_short": "Attempts: {attempts}",
        "success_rate": "{rate:.1f}% success rate",
        "interesting_fact": "Interesting fact:\nUsing the \"follow the cycle\" strategy, the success probability of all 100 prisoners is about {cycle:.0f}%, which is much higher than the random {random:.30f}%.",
        "shown_recent_stats": "Showing overall statistics for the two most recent prisoner counts.",
        "no_saved_games": "No saved games yet.",
        "unknown_export_format": "Unknown export format.",
        "export_error": "Export error: {error}",
        "file_saved": "File saved: {name}",
        "invalid_n": "Enter a valid N (from 2 to 1000).",
        "max_n": "Maximum N: 1000.",
        "save_stats_failed": "Could not save statistics to disk.",
        "new_game": "New game",
        "each": "Each",
        "cycle": "Cycle",
        "random": "Randomly",
        "prisoner_badge": "Prisoner #{number}",
        "status_round": "Prisoner: {current} / {total}\nAttempts left: {attempts}",
        "counter": "Opened: {opened}/{max_open} | Wins: {wins} | Losses: {losses}",
        "rules_title": "Game rules:",
        "rules_body": "  * Each prisoner must find their number in 100 boxes\n  * Each prisoner has 50 attempts\n  * If at least one prisoner does not find their number, everyone loses\n  * The \"Cycle\" strategy gives about a 31% chance of winning for all prisoners",
        "status_found": "Prisoner: {current} / {total}\nNumber found. Moving to the next one.",
        "status_not_found": "Prisoner: {current} / {total}\nNumber not found. Game over.",
        "status_series_done": "Prisoner: {total} / {total}\nSeries complete. Wins: {wins}, losses: {losses}.",
        "series_done_title": "Prisoner series completed",
        "series_done_summary": "Found their number: {wins}\nDid not find their number: {losses}",
        "game_over_title": "Game over: number not found in {attempts} attempts",
        "game_over_summary": "Successfully completed prisoners: {wins}\nFailed on prisoner: #{prisoner}",
        "export_pdf_title": "Prisoners Stats Export",
        "export_pdf_summary": "Summary:",
        "export_pdf_games": "Games: {value}",
        "export_pdf_wins": "Wins: {value}",
        "export_pdf_losses": "Losses: {value}",
        "export_pdf_saved": "Saved prisoners: {value}",
        "export_pdf_lost": "Lost prisoners: {value}",
        "export_pdf_win_rate": "Win rate: {value:.1f}%",
        "export_pdf_by_prisoners": "By prisoners:",
        "export_pdf_line": "N={prisoners} | games={games} | wins={wins} | losses={losses} | saved={saved} | lost={lost} | win rate={rate:.1f}%",
    },
    "ru": {
        "window_title": "100 заключенных",
        "main_title": "100 заключенных",
        "play": "Играть",
        "statistics": "Статистика",
        "exit": "Выйти",
        "main_subtitle": "Классическая логическая задача\nНайдите свой номер среди 100 ящиков",
        "game_setup": "Настройка игры",
        "prisoners_count": "Количество заключенных:",
        "enter_number": "Введите число (от 2 до 1000):",
        "attempts_per_person": "Попыток на каждого: {attempts}",
        "quick_selection": "Быстрый выбор:",
        "start_game": "Начать игру",
        "back": "Назад",
        "export_data": "Экспорт данных",
        "overall_statistics": "Общая статистика",
        "stats_by_prisoners": "Статистика по количеству заключенных",
        "stats_recent_info": "Ниже показана общая статистика для двух последних запусков.",
        "total_games": "Всего игр",
        "win_percentage": "Процент побед",
        "wins": "Побед",
        "losses": "Поражений",
        "games": "Игры",
        "total": "Всего",
        "prisoners": "Заключенные",
        "found": "Нашли",
        "lost": "Проиграли",
        "prisoners_n": "{count} заключенных",
        "attempts_short": "Попыток: {attempts}",
        "success_rate": "{rate:.1f}% успешность",
        "interesting_fact": "Интересный факт:\nПри использовании стратегии \"следования по циклу\" вероятность успеха всех 100 заключенных составляет около {cycle:.0f}%, что намного выше случайных {random:.30f}%.",
        "shown_recent_stats": "Показана общая статистика по двум последним количествам заключенных.",
        "no_saved_games": "Сохраненных игр пока нет.",
        "unknown_export_format": "Неизвестный формат экспорта.",
        "export_error": "Ошибка экспорта: {error}",
        "file_saved": "Файл сохранен: {name}",
        "invalid_n": "Введите корректное N (от 2 до 1000).",
        "max_n": "Максимальное N: 1000.",
        "save_stats_failed": "Не удалось сохранить статистику на диск.",
        "new_game": "Новая игра",
        "each": "Каждый",
        "cycle": "Цикл",
        "random": "Случайно",
        "prisoner_badge": "Заключенный #{number}",
        "status_round": "Заключенный: {current} / {total}\nПопыток осталось: {attempts}",
        "counter": "Открыто: {opened}/{max_open} | Успехи: {wins} | Поражения: {losses}",
        "rules_title": "Правила игры:",
        "rules_body": "  * Каждый заключенный должен найти свой номер в 100 ящиках\n  * У каждого заключенного есть 50 попыток\n  * Если хотя бы один заключенный не найдет свой номер - все проигрывают\n  * Стратегия \"ЦИКЛ\" дает около 31% шанса на победу для всех заключенных",
        "status_found": "Заключенный: {current} / {total}\nНомер найден. Переход к следующему.",
        "status_not_found": "Заключенный: {current} / {total}\nНомер не найден. Игра завершена.",
        "status_series_done": "Заключенный: {total} / {total}\nСерия завершена. Успехов: {wins}, поражений: {losses}.",
        "series_done_title": "Серия заключенных пройдена",
        "series_done_summary": "Успешно нашли номер: {wins}\nНе нашли номер: {losses}",
        "game_over_title": "Игра завершена: номер не найден за {attempts} попыток",
        "game_over_summary": "Успешно пройдено заключенных: {wins}\nПровал на заключенном: #{prisoner}",
        "export_pdf_title": "Prisoners Stats Export",
        "export_pdf_summary": "Summary:",
        "export_pdf_games": "Games: {value}",
        "export_pdf_wins": "Wins: {value}",
        "export_pdf_losses": "Losses: {value}",
        "export_pdf_saved": "Saved prisoners: {value}",
        "export_pdf_lost": "Lost prisoners: {value}",
        "export_pdf_win_rate": "Win rate: {value:.1f}%",
        "export_pdf_by_prisoners": "By prisoners:",
        "export_pdf_line": "N={prisoners} | games={games} | wins={wins} | losses={losses} | saved={saved} | lost={lost} | win rate={rate:.1f}%",
    },
    "ky": {
        "window_title": "100 туткун",
        "main_title": "100 туткун",
        "play": "Оюн",
        "statistics": "Статистика",
        "exit": "Чыгуу",
        "main_subtitle": "Классикалык логикалык табышмак\n100 кутучанын арасынан өз номериңди тап",
        "game_setup": "Оюнду жөндөө",
        "prisoners_count": "Түрмөгө камалгандардын саны:",
        "enter_number": "Санды киргизиңиз (2 ден 1000 ге чейин):",
        "attempts_per_person": "Ар бирине аракеттер: {attempts}",
        "quick_selection": "Ылдам тандоо:",
        "start_game": "Оюнду баштоо",
        "back": "Артка",
        "export_data": "Маалыматтарды экспорттоо",
        "overall_statistics": "Жалпы статистика",
        "stats_by_prisoners": "Камактагы адамдардын статистикасы",
        "stats_recent_info": "Төмөндө акыркы эки түрмө саны боюнча жалпы статистика көрсөтүлөт.",
        "total_games": "Бардык оюндар",
        "win_percentage": "Жеңиш пайызы",
        "wins": "Жеңиштер",
        "losses": "Жеңилүүлөр",
        "games": "Оюндар",
        "total": "Бардык",
        "prisoners": "Камактагы адамдар",
        "found": "Тапты",
        "lost": "Жоготту",
        "prisoners_n": "{count} камактагы адам",
        "attempts_short": "Таркет: {attempts}",
        "success_rate": "{rate:.1f}% ийгиликтүүлүк",
        "interesting_fact": "Кызыктуу факт:\n\"Цикл боюнча следование\" стратегиясын колдонгондо, 100 камактагы адамдын ийгилик мүмкүнчүлүгү болжол менен {cycle:.0f}% түзөт, бул кокустуктан {random:.30f}% кыйла жогору.",
        "shown_recent_stats": "Акыркы эки түрмө саны боюнча жалпы статистика көрсөтүлдү.",
        "no_saved_games": "Сакталган оюндар азырынча жок.",
        "unknown_export_format": "Экспорт форматы белгисиз.",
        "export_error": "Экспорт катасы: {error}",
        "file_saved": "Файл сакталды: {name}",
        "invalid_n": "Туура N киргизиңиз (2 ден 1000 ге чейин).",
        "max_n": "Максималдуу N: 1000.",
        "save_stats_failed": "Статистиканы дискке сактоо мүмкүн болгон жок.",
        "new_game": "Жаңы оюн",
        "each": "Ар бир",
        "cycle": "Цикл",
        "random": "Кокусунан",
        "prisoner_badge": "Түрмөдөгү #{number}",
        "status_round": "Түрмөдөгү: {current} / {total}\nАракет калды: {attempts}",
        "counter": "Ачылды: {opened}/{max_open} | Жеңиштер: {wins} | Жеңилүүлөр: {losses}",
        "rules_title": "Оюндун эрежелери:",
        "rules_body": "  * Ар бир түрмөдөгү адам 100 кутучадан өз номерин табышы керек\n  * Ар бир түрмөдөгү адамда 50 аракет бар\n  * Эгерде бир түрмөдөгү адам өз номерин таппаса - баары утулат\n  * \"Цикл\" стратегиясы бардык түрмөдөгү адамдар үчүн ~31% жеңиш мүмкүнчүлүгүн берет",
        "status_found": "Түрмөдөгү: {current} / {total}\nНомер табылды. Кийинкисине өтүү.",
        "status_not_found": "Түрмөдөгү: {current} / {total}\nНомер табылган жок. Оюн аяктады.",
        "status_series_done": "Түрмөдөгү: {total} / {total}\nСерия аяктады. Жеңиштер: {wins}, жеңилүүлөр: {losses}.",
        "series_done_title": "Түрмөдөгүлөрдүн сериясы аяктады",
        "series_done_summary": "Номерин тапкандар: {wins}\nТаппай калгандар: {losses}",
        "game_over_title": "Оюн аяктады: номер {attempts} аракетте табылган жок",
        "game_over_summary": "Ийгиликтүү өткөндөр: {wins}\nКата кеткен түрмөдөгү: #{prisoner}",
        "export_pdf_title": "Prisoners Stats Export",
        "export_pdf_summary": "Summary:",
        "export_pdf_games": "Games: {value}",
        "export_pdf_wins": "Wins: {value}",
        "export_pdf_losses": "Losses: {value}",
        "export_pdf_saved": "Saved prisoners: {value}",
        "export_pdf_lost": "Lost prisoners: {value}",
        "export_pdf_win_rate": "Win rate: {value:.1f}%",
        "export_pdf_by_prisoners": "By prisoners:",
        "export_pdf_line": "N={prisoners} | games={games} | wins={wins} | losses={losses} | saved={saved} | lost={lost} | win rate={rate:.1f}%",
    },
}


class PrisonersApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.language = "ru"
        self.current_screen = "main_menu"
        self.title(self.t("window_title"))
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

        self.stats_kpi_labels: Dict[str, ctk.CTkLabel] = {}
        self.stats_n_cards: Dict[int, Dict[str, ctk.CTkLabel]] = {}
        self.stats_fact_label: Optional[ctk.CTkLabel] = None
        self.export_status_label: Optional[ctk.CTkLabel] = None
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
        self.setup_summary_value_label: Optional[ctk.CTkLabel] = None
        self.setup_summary_attempts_label: Optional[ctk.CTkLabel] = None
        self.quick_pick_buttons: List[ctk.CTkButton] = []
        self.mode_buttons: Dict[str, ctk.CTkButton] = {}
        self.game_mode = "manual"
        self.auto_job: Optional[str] = None
        self.auto_sequence: List[int] = []
        self.auto_step_index = 0
        self.timer_job: Optional[str] = None
        self.timer_started_at: Optional[float] = None
        self.icon_images: Dict[str, object] = {}

        self.show_main_menu()

    def t(self, key: str, **kwargs) -> str:
        text = TRANSLATIONS.get(self.language, TRANSLATIONS["ru"]).get(key, key)
        return text.format(**kwargs) if kwargs else text

    def set_language(self, language: str) -> None:
        if language not in TRANSLATIONS or language == self.language:
            return
        self.language = language
        self.title(self.t("window_title"))
        if self.current_screen == "main_menu":
            self.show_main_menu()
        elif self.current_screen == "game_setup":
            self.show_game_setup()
        elif self.current_screen == "stats":
            self.show_stats_page()
        elif self.current_screen == "export":
            self.show_export_page()

    def _render_language_switcher(self, parent) -> None:
        wrap = ctk.CTkFrame(parent, fg_color="#9a9a9a", corner_radius=6)
        wrap.place(relx=0.955, rely=0.012, anchor="ne")

        for idx, (code, label) in enumerate(LANGUAGE_OPTIONS):
            is_active = code == self.language
            self._make_button(
                wrap,
                label,
                command=lambda lang=code: self.set_language(lang),
                fg_color="#a7a7a7" if is_active else "#dddddd",
                hover_color="#cfcfcf",
                width=100,
                height=23,
                font_size=11,
                corner_radius=4,
                text_color="#111111",
                bold=True,
            ).pack(padx=1, pady=(1, 0) if idx == 0 else (0, 1))

    def clear_container(self) -> None:
        self._cancel_auto_job()
        self._cancel_timer_job()
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
        self.export_status_label = None

    def _record_completed_game(self, won: bool, total_prisoners: int, saved_prisoners: int) -> None:
        try:
            self.stats_store.record_game(
                won=won,
                total_prisoners=total_prisoners,
                saved_prisoners=saved_prisoners,
            )
            self.stats_store.save()
        except Exception:
            self._set_status(self.t("save_stats_failed"), "#ffb0b0")

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

    def _text_font(self, size: int, *, bold: bool = False) -> ctk.CTkFont:
        return ctk.CTkFont(
            family=TEXT_FONT_FAMILY,
            size=size,
            weight="bold" if bold else "normal",
        )

    def _number_font(self, size: int, *, bold: bool = False) -> ctk.CTkFont:
        return ctk.CTkFont(
            family=NUMBER_FONT_FAMILY,
            size=size,
            weight="bold" if bold else "normal",
        )

    def _make_people_badge(self, parent) -> ctk.CTkFrame:
        badge = ctk.CTkFrame(parent, fg_color="transparent", width=86, height=44)
        badge.pack(side="left")
        badge.pack_propagate(False)

        canvas = tk.Canvas(
            badge,
            width=86,
            height=44,
            bg=BG_COLOR,
            highlightthickness=0,
            bd=0,
        )
        canvas.pack(fill="both", expand=True)

        def _rounded_rect(x1: int, y1: int, x2: int, y2: int, radius: int, fill: str) -> None:
            canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill=fill, outline=fill)
            canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, fill=fill, outline=fill)
            canvas.create_oval(x1, y1, x1 + radius * 2, y1 + radius * 2, fill=fill, outline=fill)
            canvas.create_oval(x2 - radius * 2, y1, x2, y1 + radius * 2, fill=fill, outline=fill)
            canvas.create_oval(x1, y2 - radius * 2, x1 + radius * 2, y2, fill=fill, outline=fill)
            canvas.create_oval(x2 - radius * 2, y2 - radius * 2, x2, y2, fill=fill, outline=fill)

        badge_fill = "#1608ff"
        stroke = "#eef2ff"
        _rounded_rect(2, 2, 84, 42, 20, badge_fill)

        canvas.create_oval(28, 10, 43, 25, outline=stroke, width=2)
        canvas.create_arc(18, 22, 54, 46, start=15, extent=150, style="arc", outline=stroke, width=2)

        canvas.create_oval(46, 12, 58, 24, outline=stroke, width=1)
        canvas.create_arc(40, 23, 67, 43, start=18, extent=144, style="arc", outline=stroke, width=1)

        return badge

    def _get_icon(self, name: str, size: tuple[int, int], color: str) -> object | None:
        key = f"{name}:{size[0]}:{size[1]}:{color}"
        if key in self.icon_images:
            return self.icon_images[key]

        if Image is None or cairosvg is None:
            return None

        icon_path = ASSETS_DIR / f"{name}.svg"
        if not icon_path.exists():
            return None

        try:
            svg_text = icon_path.read_text(encoding="utf-8").replace("currentColor", color)
            png_bytes = cairosvg.svg2png(
                bytestring=svg_text.encode("utf-8"),
                output_width=size[0],
                output_height=size[1],
            )
            image = ctk.CTkImage(
                light_image=Image.open(BytesIO(png_bytes)),
                dark_image=Image.open(BytesIO(png_bytes)),
                size=size,
            )
        except Exception:
            return None

        self.icon_images[key] = image
        return image

    def _button_label(self, text: str, icon_name: str, size: tuple[int, int], color: str) -> tuple[str, object | None]:
        icon = self._get_icon(icon_name, size, color)
        if icon is not None:
            return text, icon
        return text, None

    def _icon_only(self, icon_name: str, size: tuple[int, int], color: str) -> object | None:
        return self._get_icon(icon_name, size, color)

    def _make_icon_label(
        self,
        parent,
        *,
        icon_name: str,
        size: tuple[int, int],
        color: str,
        fallback_text: str = "",
        **kwargs,
    ) -> ctk.CTkLabel:
        icon = self._get_icon(icon_name, size, color)
        return ctk.CTkLabel(
            parent,
            text="" if icon is not None else fallback_text,
            image=icon,
            **kwargs,
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
        numeric: bool = False,
        corner_radius: int = 12,
        text_color: str = TEXT_PRIMARY,
        image=None,
        compound: str = "left",
        anchor: str = "center",
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
            font=self._number_font(font_size, bold=bold) if numeric else self._text_font(font_size, bold=bold),
            image=image,
            compound=compound,
            anchor=anchor,
        )

    def show_main_menu(self) -> None:
        self.current_screen = "main_menu"
        self.clear_container()
        self.title(self.t("window_title"))
        self._render_language_switcher(self.container)

        card = self._make_panel(self.container, fg_color=SURFACE_COLOR, corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(padx=68, pady=36)

        ctk.CTkLabel(
            content,
            text=self.t("main_title"),
            font=self._text_font(28),
            text_color=TEXT_PRIMARY,
        ).pack(pady=(0, 18))

        play_text, play_icon = self._button_label(self.t("play"), "play", (28, 32), TEXT_PRIMARY)
        self._make_button(
            content,
            play_text,
            command=self.show_game_setup,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            width=315,
            height=68,
            font_size=26,
            image=play_icon,
        ).pack(pady=6)

        stats_text, stats_icon = self._button_label(self.t("statistics"), "stats", (30, 29), TEXT_PRIMARY)
        self._make_button(
            content,
            stats_text,
            command=self.show_stats_page,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            width=315,
            height=68,
            font_size=24,
            image=stats_icon,
        ).pack(pady=6)

        exit_text, exit_icon = self._button_label(self.t("exit"), "exit", (24, 28), TEXT_PRIMARY)
        self._make_button(
            content,
            exit_text,
            command=self.destroy,
            fg_color=RED,
            hover_color=RED_HOVER,
            width=315,
            height=68,
            font_size=24,
            image=exit_icon,
        ).pack(pady=6)

        ctk.CTkLabel(
            content,
            text=self.t("main_subtitle"),
            font=self._text_font(16),
            text_color=TEXT_MUTED,
            justify="center",
        ).pack(pady=(18, 0))

    def show_game_setup(self) -> None:
        self.current_screen = "game_setup"
        self.clear_container()
        self.title(self.t("window_title"))

        panel = self._make_panel(self.container, fg_color=SURFACE_COLOR, corner_radius=20)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        body = ctk.CTkFrame(panel, fg_color="transparent")
        body.pack(padx=34, pady=28)

        ctk.CTkLabel(
            body,
            text=self.t("game_setup"),
            font=self._text_font(36, bold=True),
            text_color=TEXT_PRIMARY,
        ).pack(pady=(0, 24))

        title_row = ctk.CTkFrame(body, fg_color="transparent")
        title_row.pack(fill="x", pady=(0, 12))

        setup_icon = self._icon_only("number_of_prisoners", (30, 26), "#292929")
        if setup_icon is not None:
            ctk.CTkLabel(
                title_row,
                text="",
                image=setup_icon,
                fg_color="transparent",
            ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            title_row,
            text=self.t("prisoners_count"),
            font=self._text_font(22, bold=True),
            text_color="#0c1110",
        ).pack(side="left")

        input_card = self._make_panel(body, fg_color=SURFACE_DARK, corner_radius=10, border_width=0)
        input_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            input_card,
            text=self.t("enter_number"),
            font=self._text_font(13, bold=True),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(12, 6))

        self.cells_entry = ctk.CTkEntry(
            input_card,
            width=220,
            height=44,
            justify="center",
            font=self._number_font(24, bold=True),
            fg_color="#547d72",
            border_color="#91a89c",
            text_color=TEXT_PRIMARY,
        )
        self.cells_entry.pack(pady=(0, 18))
        self.cells_entry.insert(0, str(DEFAULT_CELLS))
        self.cells_entry.bind("<KeyRelease>", lambda _event: self._refresh_setup_preview())

        summary_card = self._make_panel(body, fg_color=SURFACE_DARK, corner_radius=10, border_width=0)
        summary_card.pack(fill="x", pady=(0, 18))

        self.setup_summary_value_label = ctk.CTkLabel(
            summary_card,
            text="100",
            font=self._number_font(24, bold=True),
            text_color="#19ff22",
            justify="center",
        )
        self.setup_summary_value_label.pack(pady=(12, 2))

        self.setup_summary_attempts_label = ctk.CTkLabel(
            summary_card,
            text=self.t("attempts_per_person", attempts=50),
            font=self._text_font(15),
            text_color=TEXT_MUTED,
            justify="center",
        )
        self.setup_summary_attempts_label.pack(pady=(0, 12))

        ctk.CTkLabel(
            body,
            text=self.t("quick_selection"),
            font=self._text_font(16),
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
                numeric=True,
                corner_radius=6,
            )
            btn.grid(row=row, column=col, padx=8, pady=6)
            self.quick_pick_buttons.append(btn)

        start_text, start_icon = self._button_label(self.t("start_game"), "play2.0", (28, 32), TEXT_PRIMARY)
        self._make_button(
            body,
            start_text,
            command=self.start_interactive_game,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            width=315,
            height=66,
            font_size=24,
            bold=True,
            image=start_icon,
        ).pack(pady=(2, 10))

        back_text, back_icon = self._button_label(self.t("back"), "back", (22, 14), TEXT_PRIMARY)
        self._make_button(
            body,
            back_text,
            command=self.show_main_menu,
            fg_color=RED,
            hover_color=RED_HOVER,
            width=315,
            height=40,
            font_size=18,
            image=back_icon,
        ).pack()

        self.status_label = ctk.CTkLabel(
            self.container,
            text="",
            font=self._text_font(15, bold=True),
            text_color="#ffb0b0",
        )
        self.status_label.pack(side="bottom", pady=(0, 10))
        self.counter_label = ctk.CTkLabel(self.container, text="")
        self._refresh_setup_preview()

    def show_stats_page(self) -> None:
        self.current_screen = "stats"
        self.clear_container()
        self.title(self.t("window_title"))

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

        back_text, back_icon = self._button_label(self.t("back"), "back", (22, 14), TEXT_PRIMARY)
        self._make_button(
            top_row,
            back_text,
            command=self.show_main_menu,
            fg_color=RED,
            hover_color=RED_HOVER,
            width=96,
            height=28,
            font_size=12,
            corner_radius=8,
            image=back_icon,
        ).pack(side="left")

        export_text, export_icon = self._button_label(self.t("export_data"), "export", (16, 20), TEXT_PRIMARY)
        self._make_button(
            top_row,
            export_text,
            command=self.show_export_page,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            width=132,
            height=28,
            font_size=12,
            corner_radius=8,
            image=export_icon,
        ).pack(side="right")

        ctk.CTkLabel(
            header,
            text=self.t("statistics"),
            font=self._text_font(38, bold=True),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=54, pady=(0, 6))

        ctk.CTkLabel(
            header,
            text=self.t("overall_statistics"),
            font=self._text_font(18, bold=True),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=64, pady=(0, 14))

        self.status_label = ctk.CTkLabel(
            header,
            text="",
            font=self._text_font(13, bold=True),
            text_color=TEXT_MUTED,
        )
        self.status_label.pack(anchor="w", padx=64, pady=(0, 8))

        kpi_row = ctk.CTkFrame(header, fg_color="transparent")
        kpi_row.pack(fill="x", padx=52, pady=(0, 22))
        kpi_row.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.stats_kpi_labels = {}

        def _kpi_card(col: int, title: str, key: str, color: str) -> None:
            card_color = color
            if key == "wins":
                card_color = "#449D5D"
            elif key == "losses":
                card_color = "#8C4B43"

            card = self._make_panel(kpi_row, fg_color=card_color, corner_radius=10, border_width=1, border_color=color)
            card.grid(row=0, column=col, padx=5, sticky="nsew")
            icon_map = {
                "games": "whole_games",
                "win_rate": "stats_win_percentage",
                "wins": "win_stats",
                "losses": "lost_stats",
            }
            if key in {"wins", "losses"}:
                content = ctk.CTkFrame(card, fg_color="transparent")
                content.pack(fill="both", expand=True, padx=12, pady=(3, 0))

                self._make_icon_label(
                    content,
                    icon_name=icon_map[key],
                    size=(38, 38) if key == "losses" else (30, 32),
                    color=color,
                    fallback_text="",
                    fg_color="transparent",
                ).pack(side="left", padx=(0, 10))

                text_wrap = ctk.CTkFrame(content, fg_color="transparent")
                text_wrap.pack(side="left", fill="both", expand=True)
                text_wrap.grid_columnconfigure(0, weight=1)

                value_label = ctk.CTkLabel(
                    text_wrap,
                    text="0",
                    font=self._number_font(34, bold=True),
                    text_color=TEXT_PRIMARY,
                )
                value_label.pack(anchor="center", pady=(8, 0))
                ctk.CTkLabel(
                    text_wrap,
                    text=title,
                    font=self._text_font(14),
                    text_color=TEXT_PRIMARY,
                ).pack(anchor="center", pady=(0, 0))
            else:
                self._make_icon_label(
                    card,
                    icon_name=icon_map[key],
                    size=(30, 26) if key == "games" else (34, 20),
                    color="#0077ff" if key == "games" else "#48d06c",
                    fallback_text="",
                    fg_color="transparent",
                ).pack(pady=(12, 2))

                value_label = ctk.CTkLabel(
                    card,
                    text="0",
                    font=self._number_font(28, bold=True),
                    text_color=TEXT_PRIMARY,
                )
                value_label.pack(pady=(2, 2))
                ctk.CTkLabel(
                    card,
                    text=title,
                    font=self._text_font(14),
                    text_color=TEXT_MUTED,
                ).pack(pady=(0, 12))
            self.stats_kpi_labels[key] = value_label

        _kpi_card(0, self.t("total_games"), "games", "#2b584b")
        _kpi_card(1, self.t("win_percentage"), "win_rate", "#396856")
        _kpi_card(2, self.t("wins"), "wins", "#34C759")
        _kpi_card(3, self.t("losses"), "losses", "#FF0000")

        ctk.CTkLabel(
            page,
            text=self.t("stats_by_prisoners"),
            font=self._text_font(26, bold=True),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=160, pady=(12, 18))

        ctk.CTkLabel(
            page,
            text=self.t("stats_recent_info"),
            font=self._text_font(13),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=160, pady=(0, 14))

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
                font=self._number_font(12, bold=True),
                text_color=TEXT_PRIMARY,
            )
            value.pack(padx=18, pady=(6, 0))
            ctk.CTkLabel(
                chip,
                text=title,
                font=self._text_font(9),
                text_color=TEXT_MUTED,
            ).pack(padx=18, pady=(0, 6))
            return value

        def _n_card(col: int, n_value: int, border: str) -> None:
            card = self._make_panel(details_row, fg_color=SURFACE_COLOR, corner_radius=14, border_color=border)
            card.grid(row=0, column=col, padx=14, sticky="nsew")

            head = ctk.CTkFrame(card, fg_color="transparent")
            head.pack(fill="x", padx=14, pady=(10, 8))
            users_icon = self._get_icon("stats_prisoner_number", (58, 48), "#eef2ff")
            if users_icon is not None:
                ctk.CTkLabel(
                    head,
                    text="",
                    image=users_icon,
                    fg_color="transparent",
                    width=58,
                    height=48,
                ).pack(side="left")
            else:
                self._make_people_badge(head)

            title_wrap = ctk.CTkFrame(head, fg_color="transparent")
            title_wrap.pack(side="left", padx=10)

            title_label = ctk.CTkLabel(
                title_wrap,
                text=self.t("prisoners_n", count=n_value),
                font=self._text_font(17, bold=True),
                text_color=TEXT_PRIMARY,
            )
            title_label.pack(anchor="w")
            attempts_label = ctk.CTkLabel(
                title_wrap,
                text=self.t("attempts_short", attempts=n_value // 2),
                font=self._number_font(13),
                text_color=TEXT_DIM,
            )
            attempts_label.pack(anchor="w")

            ctk.CTkFrame(card, fg_color="#d8e8dd", height=1).pack(fill="x", padx=12, pady=(0, 10))

            ctk.CTkLabel(
                card,
                text=self.t("games"),
                font=self._text_font(12),
                text_color=TEXT_MUTED,
            ).pack(anchor="w", padx=14)

            games_row = ctk.CTkFrame(card, fg_color="transparent")
            games_row.pack(padx=14, pady=(8, 8))
            games_label = _stat_chip(games_row, "games", self.t("total"), "#92a59c")
            wins_label = _stat_chip(games_row, "wins", self.t("wins"), "#47a962")
            losses_label = _stat_chip(games_row, "losses", self.t("losses"), "#8a6257")

            ctk.CTkLabel(
                card,
                text=self.t("prisoners"),
                font=self._text_font(12),
                text_color=TEXT_MUTED,
            ).pack(anchor="w", padx=14, pady=(2, 0))

            prisoners_row = ctk.CTkFrame(card, fg_color="transparent")
            prisoners_row.pack(padx=14, pady=(8, 6))
            saved_label = _stat_chip(prisoners_row, "saved", self.t("found"), "#47a962")
            lost_label = _stat_chip(prisoners_row, "lost", self.t("lost"), "#8a6257")

            win_rate_label = ctk.CTkLabel(
                card,
                text=self.t("success_rate", rate=0.0),
                font=self._number_font(15),
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
            text=self.t("interesting_fact", cycle=0, random=0.0),
            font=self._text_font(15),
            text_color=TEXT_MUTED,
            justify="left",
            wraplength=760,
        )
        self.stats_fact_label.pack(anchor="w", padx=18, pady=12)

        self.run_stats()

    def show_export_page(self) -> None:
        self.current_screen = "export"
        self.clear_container()
        self.title(self.t("window_title"))

        shell = self._make_panel(self.container, fg_color=SURFACE_COLOR, corner_radius=18)
        shell.place(relx=0.5, rely=0.5, anchor="center")

        body = ctk.CTkFrame(shell, fg_color="transparent")
        body.pack(padx=90, pady=58)

        title_pill = ctk.CTkFrame(body, fg_color="#6d9786", corner_radius=20)
        title_pill.pack(pady=(0, 42))

        export_icon = self._icon_only("export", (18, 22), TEXT_PRIMARY)
        title_row = ctk.CTkFrame(title_pill, fg_color="transparent")
        title_row.pack(padx=26, pady=10)
        if export_icon is not None:
            ctk.CTkLabel(
                title_row,
                text="",
                image=export_icon,
                fg_color="transparent",
            ).pack(side="left", padx=(0, 14))
        ctk.CTkLabel(
            title_row,
            text=self.t("export_data"),
            font=self._text_font(28, bold=True),
            text_color="#b8ff84",
        ).pack(side="left")

        center_card = ctk.CTkFrame(body, fg_color="#1f5637", corner_radius=14, width=370, height=480)
        center_card.pack()
        center_card.pack_propagate(False)

        buttons_wrap = ctk.CTkFrame(center_card, fg_color="transparent")
        buttons_wrap.pack(fill="x", padx=20, pady=46)

        export_buttons = [
            ("XLSX", "#29a643", "#238f39", "xlsx"),
            ("PDF", "#b3473d", "#9d3e36", "pdf"),
            ("CSV", "#3a834e", "#327245", "csv"),
            ("XML", "#b18120", "#9d711b", "xml"),
            ("JSON", "#1f7fbc", "#1a6c9f", "json"),
        ]
        for text, fg, hover, fmt in export_buttons:
            self._make_button(
                buttons_wrap,
                text,
                command=lambda f=fmt: self._export_stats(f),
                fg_color=fg,
                hover_color=hover,
                width=330,
                height=56,
                font_size=26,
                bold=True,
                text_color="#0a0f0d" if fmt != "pdf" else TEXT_PRIMARY,
            ).pack(pady=8)

        self.export_status_label = ctk.CTkLabel(
            body,
            text="",
            font=self._text_font(14, bold=True),
            text_color=TEXT_MUTED,
            justify="center",
        )
        self.export_status_label.pack(pady=(18, 8))

        bottom_row = ctk.CTkFrame(body, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(8, 0))
        self._make_button(
            bottom_row,
            self.t("back"),
            command=self.show_stats_page,
            fg_color=RED,
            hover_color=RED_HOVER,
            width=140,
            height=38,
            font_size=18,
            image=self._icon_only("back", (22, 14), TEXT_PRIMARY),
        ).pack()

    def _set_export_status(self, text: str, color: str = TEXT_MUTED) -> None:
        if self.export_status_label:
            self.export_status_label.configure(text=text, text_color=color)

    def _build_export_payload(self) -> Dict[str, object]:
        total_summary = self.stats_store.total_summary()
        details: Dict[str, Dict[str, float]] = {}
        counts = sorted(set(DEFAULT_STATS_COUNTS + self.stats_detail_ns))
        for n_value in counts:
            details[str(n_value)] = self.stats_store.summary_for_n(n_value)
        return {"summary": total_summary, "by_prisoners": details}

    def _build_export_rows(self, payload: Dict[str, object]) -> List[Dict[str, object]]:
        rows = [{"scope": "summary", "prisoners": "all", **payload["summary"]}]
        for n_key, stats in payload["by_prisoners"].items():
            rows.append({"scope": "by_prisoners", "prisoners": n_key, **stats})
        return rows

    def _export_stats_xlsx(self, target: Path, rows: List[Dict[str, object]]) -> None:
        def col_name(index: int) -> str:
            name = ""
            value = index
            while value > 0:
                value, remainder = divmod(value - 1, 26)
                name = chr(65 + remainder) + name
            return name

        def xml_escape(value: object) -> str:
            text = str(value)
            return (
                text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )

        worksheet_rows: List[str] = []
        all_rows = [EXPORT_HEADERS] + [[row.get(header, "") for header in EXPORT_HEADERS] for row in rows]
        for row_index, row_values in enumerate(all_rows, start=1):
            cells: List[str] = []
            for col_index, value in enumerate(row_values, start=1):
                cell_ref = f"{col_name(col_index)}{row_index}"
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    cells.append(f'<c r="{cell_ref}"><v>{value}</v></c>')
                else:
                    cells.append(
                        f'<c r="{cell_ref}" t="inlineStr"><is><t>{xml_escape(value)}</t></is></c>'
                    )
            worksheet_rows.append(f"<row r=\"{row_index}\">{''.join(cells)}</row>")

        worksheet_xml = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">"
            "<sheetData>"
            f"{''.join(worksheet_rows)}"
            "</sheetData>"
            "</worksheet>"
        )

        workbook_xml = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" "
            "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">"
            "<sheets>"
            "<sheet name=\"Stats\" sheetId=\"1\" r:id=\"rId1\"/>"
            "</sheets>"
            "</workbook>"
        )

        workbook_rels_xml = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
            "<Relationship Id=\"rId1\" "
            "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" "
            "Target=\"worksheets/sheet1.xml\"/>"
            "<Relationship Id=\"rId2\" "
            "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" "
            "Target=\"styles.xml\"/>"
            "</Relationships>"
        )

        package_rels_xml = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
            "<Relationship Id=\"rId1\" "
            "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" "
            "Target=\"xl/workbook.xml\"/>"
            "</Relationships>"
        )

        content_types_xml = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
            "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"
            "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"
            "<Override PartName=\"/xl/workbook.xml\" "
            "ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/>"
            "<Override PartName=\"/xl/worksheets/sheet1.xml\" "
            "ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>"
            "<Override PartName=\"/xl/styles.xml\" "
            "ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml\"/>"
            "</Types>"
        )

        styles_xml = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<styleSheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">"
            "<fonts count=\"1\"><font><sz val=\"11\"/><name val=\"Calibri\"/></font></fonts>"
            "<fills count=\"1\"><fill><patternFill patternType=\"none\"/></fill></fills>"
            "<borders count=\"1\"><border><left/><right/><top/><bottom/><diagonal/></border></borders>"
            "<cellStyleXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\"/></cellStyleXfs>"
            "<cellXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\"/></cellXfs>"
            "<cellStyles count=\"1\"><cellStyle name=\"Normal\" xfId=\"0\" builtinId=\"0\"/></cellStyles>"
            "</styleSheet>"
        )

        with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", content_types_xml)
            archive.writestr("_rels/.rels", package_rels_xml)
            archive.writestr("xl/workbook.xml", workbook_xml)
            archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
            archive.writestr("xl/worksheets/sheet1.xml", worksheet_xml)
            archive.writestr("xl/styles.xml", styles_xml)

    def _export_stats_pdf(self, target: Path, rows: List[Dict[str, object]]) -> None:
        def pdf_escape(value: object) -> str:
            return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

        lines = [
            self.t("export_pdf_title"),
            "",
            self.t("export_pdf_summary"),
        ]
        summary_row = rows[0] if rows else {}
        lines.extend(
            [
                self.t("export_pdf_games", value=summary_row.get("games", 0)),
                self.t("export_pdf_wins", value=summary_row.get("wins", 0)),
                self.t("export_pdf_losses", value=summary_row.get("losses", 0)),
                self.t("export_pdf_saved", value=summary_row.get("saved_prisoners", 0)),
                self.t("export_pdf_lost", value=summary_row.get("lost_prisoners", 0)),
                self.t("export_pdf_win_rate", value=summary_row.get("win_rate", 0)),
                "",
                self.t("export_pdf_by_prisoners"),
            ]
        )

        for row in rows[1:]:
            lines.append(
                self.t(
                    "export_pdf_line",
                    prisoners=row.get("prisoners"),
                    games=row.get("games"),
                    wins=row.get("wins"),
                    losses=row.get("losses"),
                    saved=row.get("saved_prisoners"),
                    lost=row.get("lost_prisoners"),
                    rate=float(row.get("win_rate", 0)),
                )
            )

        max_lines_per_page = 40
        pages = [lines[i:i + max_lines_per_page] for i in range(0, len(lines), max_lines_per_page)] or [[]]

        font_id = 1
        content_ids = [2 + index * 2 for index in range(len(pages))]
        page_ids = [content_id + 1 for content_id in content_ids]
        pages_id = 2 + len(pages) * 2
        catalog_id = pages_id + 1

        objects: List[bytes] = [b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
        for page_index, page_lines in enumerate(pages):
            text_lines = ["BT", "/F1 12 Tf", "50 790 Td", "14 TL"]
            first_text = True
            for line in page_lines:
                operator = "Tj" if first_text else "'"
                text_lines.append(f"({pdf_escape(line)}) {operator}")
                first_text = False
            text_lines.append("ET")
            stream = "\n".join(text_lines).encode("latin-1")
            objects.append(
                b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream"
            )
            objects.append(
                (
                    f"<< /Type /Page /Parent {pages_id} 0 R "
                    f"/MediaBox [0 0 595 842] "
                    f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
                    f"/Contents {content_ids[page_index]} 0 R >>"
                ).encode("ascii")
            )

        kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
        objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii"))
        objects.append(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("ascii"))

        pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for index, obj in enumerate(objects, start=1):
            offsets.append(len(pdf))
            pdf.extend(f"{index} 0 obj\n".encode("ascii"))
            pdf.extend(obj)
            pdf.extend(b"\nendobj\n")

        xref_offset = len(pdf)
        pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        pdf.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
        pdf.extend(
            (
                f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
                f"startxref\n{xref_offset}\n%%EOF"
            ).encode("ascii")
        )
        target.write_bytes(pdf)

    def _export_stats(self, fmt: str) -> None:
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        payload = self._build_export_payload()
        rows = self._build_export_rows(payload)

        try:
            if fmt == "json":
                target = EXPORTS_DIR / "prisoners_stats_export.json"
                target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            elif fmt == "csv":
                target = EXPORTS_DIR / "prisoners_stats_export.csv"
                with target.open("w", encoding="utf-8", newline="") as fh:
                    writer = DictWriter(
                        fh,
                        fieldnames=EXPORT_HEADERS,
                    )
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(row)
            elif fmt == "xml":
                target = EXPORTS_DIR / "prisoners_stats_export.xml"
                root = ET.Element("stats")
                summary_node = ET.SubElement(root, "summary")
                for key, value in payload["summary"].items():
                    ET.SubElement(summary_node, key).text = str(value)
                by_prisoners_node = ET.SubElement(root, "by_prisoners")
                for n_key, stats in payload["by_prisoners"].items():
                    item_node = ET.SubElement(by_prisoners_node, "group", prisoners=n_key)
                    for key, value in stats.items():
                        ET.SubElement(item_node, key).text = str(value)
                ET.ElementTree(root).write(target, encoding="utf-8", xml_declaration=True)
            elif fmt == "xlsx":
                target = EXPORTS_DIR / "prisoners_stats_export.xlsx"
                self._export_stats_xlsx(target, rows)
            elif fmt == "pdf":
                target = EXPORTS_DIR / "prisoners_stats_export.pdf"
                self._export_stats_pdf(target, rows)
            else:
                self._set_export_status(self.t("unknown_export_format"), "#ffb0b0")
                return
        except Exception as exc:
            self._set_export_status(self.t("export_error", error=exc), "#ffb0b0")
            return

        self._set_export_status(self.t("file_saved", name=target.name), "#b8ff84")

    def _parse_positive_int(self, text: str) -> Optional[int]:
        value = text.strip()
        if not value.isdigit():
            return None
        number = int(value)
        if number <= 1:
            return None
        return number

    def _refresh_setup_preview(self) -> None:
        if not self.cells_entry or not self.setup_summary_value_label or not self.setup_summary_attempts_label:
            return

        value = self.cells_entry.get().strip()
        n = int(value) if value.isdigit() else 0
        attempts = n // 2 if n >= 2 else 0
        self.setup_summary_value_label.configure(
            text=str(n),
            text_color="#19ff22" if n >= 2 else TEXT_MUTED,
        )
        self.setup_summary_attempts_label.configure(text=self.t("attempts_per_person", attempts=attempts))

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
                self._set_status(self.t("invalid_n"), "#ffb0b0")
                return
            if n > 1000:
                self._set_status(self.t("max_n"), "#ffb0b0")
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
        self.timer_started_at = None

        self._show_gameplay_screen()
        self._start_timer()
        self._start_round()

    def _show_gameplay_screen(self) -> None:
        self.current_screen = "gameplay"
        self.clear_container()
        self.title(self.t("window_title"))

        self.game_header = self._make_panel(self.container, fg_color=SURFACE_COLOR, corner_radius=12)
        self.game_header.pack(fill="x", padx=8, pady=(4, 10))

        header_top = ctk.CTkFrame(self.game_header, fg_color="transparent")
        header_top.pack(fill="x", padx=10, pady=(10, 8))

        back_text, back_icon = self._button_label(self.t("back"), "back", (20, 12), TEXT_PRIMARY)
        self._make_button(
            header_top,
            back_text,
            command=self.show_game_setup,
            fg_color=RED,
            hover_color=RED_HOVER,
            width=88,
            height=26,
            font_size=11,
            corner_radius=8,
            image=back_icon,
        ).pack(side="left")

        right_controls = ctk.CTkFrame(header_top, fg_color="transparent")
        right_controls.pack(side="right")

        timer_icon = self._get_icon("timer", (14, 16), "#053047")
        self.game_attempts_value = ctk.CTkLabel(
            right_controls,
            text="0:00",
            image=timer_icon,
            font=self._number_font(11),
            text_color=TEXT_PRIMARY,
            fg_color="#1ab8b0",
            corner_radius=8,
            width=68,
            height=24,
            compound="left",
        )
        self.game_attempts_value.pack(side="left", padx=(0, 8))

        new_text, new_icon = self._button_label(self.t("new_game"), "restart", (18, 16), TEXT_PRIMARY)
        self._make_button(
            right_controls,
            new_text,
            command=self.start_interactive_game,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            width=108,
            height=24,
            font_size=11,
            corner_radius=8,
            image=new_icon,
        ).pack(side="left")

        info_row = ctk.CTkFrame(self.game_header, fg_color="transparent")
        info_row.pack(fill="x", padx=12, pady=(0, 6))

        self.status_label = ctk.CTkLabel(
            info_row,
            text="",
            font=self._text_font(12),
            text_color=TEXT_PRIMARY,
            justify="left",
        )
        self.status_label.pack(anchor="w")

        self.counter_label = ctk.CTkLabel(
            info_row,
            text="",
            font=self._text_font(12),
            text_color=TEXT_MUTED,
            justify="left",
        )
        self.counter_label.pack(anchor="w", pady=(2, 8))

        mode_row = ctk.CTkFrame(self.game_header, fg_color="transparent")
        mode_row.pack(anchor="e", padx=12, pady=(0, 10))

        self.mode_buttons = {}
        mode_specs = [("manual", self.t("each")), ("cycle", self.t("cycle")), ("random", self.t("random"))]
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

        avatar_icon = self._get_icon("prisoner_icon", (88, 108), TEXT_PRIMARY)
        ctk.CTkLabel(
            self.game_prisoner_card,
            text="P" if avatar_icon is None else "",
            image=avatar_icon,
            font=self._text_font(46, bold=True),
            text_color="#ff9933",
            width=110,
            height=126,
            fg_color="transparent",
            corner_radius=10,
        ).pack(pady=(18, 8))

        self.prisoner_badge_label = ctk.CTkLabel(
            self.game_prisoner_card,
            text=self.t("prisoner_badge", number=1),
            font=self._text_font(14),
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
        if mode not in {"manual", *AUTO_MODES}:
            return
        if mode == self.game_mode:
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

    def _cancel_timer_job(self) -> None:
        if self.timer_job is not None:
            try:
                self.after_cancel(self.timer_job)
            except Exception:
                pass
            self.timer_job = None

    def _format_elapsed_time(self) -> str:
        if self.timer_started_at is None:
            return "0:00"
        elapsed = max(0, int(time.monotonic() - self.timer_started_at))
        minutes, seconds = divmod(elapsed, 60)
        return f"{minutes}:{seconds:02d}"

    def _update_timer_label(self) -> None:
        if self.game_attempts_value:
            self.game_attempts_value.configure(text=self._format_elapsed_time())

    def _tick_timer(self) -> None:
        self.timer_job = None
        self._update_timer_label()
        if self.timer_started_at is not None:
            self.timer_job = self.after(1000, self._tick_timer)

    def _start_timer(self) -> None:
        self._cancel_timer_job()
        self.timer_started_at = time.monotonic()
        self._update_timer_label()
        self.timer_job = self.after(1000, self._tick_timer)

    def _build_cycle_sequence(self) -> List[int]:
        sequence: List[int] = []
        current_idx = self.prisoner_number - 1
        for _ in range(self.max_open):
            sequence.append(current_idx)
            found_number = self.boxes[current_idx]
            if found_number == self.prisoner_number:
                break
            current_idx = found_number - 1
        return sequence

    def _prepare_auto_sequence(self) -> None:
        self.auto_step_index = 0
        if self.game_mode == "cycle":
            self.auto_sequence = self._build_cycle_sequence()
            return

        if self.game_mode == "random":
            self.auto_sequence = random.sample(range(self.total_cells), k=self.max_open)
            return

        self.auto_sequence = []

    def _schedule_auto_step(self) -> None:
        self._cancel_auto_job()
        if self.game_mode not in AUTO_MODES:
            return
        self.auto_job = self.after(25, self._auto_step)

    def _auto_step(self) -> None:
        self.auto_job = None
        if self.game_finished or self.game_mode not in AUTO_MODES:
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
            self.t(
                "status_round",
                current=self.prisoner_number,
                total=self.total_cells,
                attempts=self.max_open,
            ),
            TEXT_PRIMARY,
        )
        self._update_counter()
        if self.board_wrap is None or len(self.cell_buttons) != self.total_cells:
            self.render_game_board()
        else:
            self._reset_board_buttons()
        if self.prisoner_badge_label:
            self.prisoner_badge_label.configure(text=self.t("prisoner_badge", number=self.prisoner_number))
        if self.game_mode in {"cycle", "random"}:
            self._prepare_auto_sequence()
            self._schedule_auto_step()

    def _set_status(self, text: str, color: str) -> None:
        if self.status_label:
            self.status_label.configure(text=text, text_color=color)

    def _update_counter(self) -> None:
        if self.counter_label:
            self.counter_label.configure(
                text=self.t(
                    "counter",
                    opened=self.opened_count,
                    max_open=self.max_open,
                    wins=self.successful_rounds,
                    losses=self.failed_rounds,
                )
            )
        self._update_timer_label()

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
        btn_size = 60 if self.total_cells <= 100 else 52
        for col in range(cols):
            self.board_wrap.grid_columnconfigure(col, weight=1, uniform="board")

        for idx in range(self.total_cells):
            row = idx // cols
            col = idx % cols
            btn = ctk.CTkButton(
                self.board_wrap,
                text=str(idx + 1),
                width=btn_size,
                height=btn_size,
                corner_radius=6,
                fg_color=CELL_COLOR,
                hover_color=CELL_HOVER,
                text_color=TEXT_PRIMARY,
                font=self._number_font(16, bold=True),
            )
            btn.configure(command=lambda i=idx, b=btn: self.open_cell(i, b))
            btn.grid(row=row, column=col, padx=1, pady=1)
            self.cell_buttons.append(btn)

        if self.game_rules_card is not None:
            self.game_rules_card.pack(fill="x", padx=8, pady=(0, 2))
            ctk.CTkLabel(
                self.game_rules_card,
                text=f"{self.t('rules_title')}\n\n{self.t('rules_body')}",
                font=self._text_font(15),
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
                self.t(
                    "status_found",
                    current=self.prisoner_number,
                    total=self.total_cells,
                ),
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
                self.t(
                    "status_not_found",
                    current=self.prisoner_number,
                    total=self.total_cells,
                ),
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
            self.t("status_series_done", total=total, wins=self.successful_rounds, losses=self.failed_rounds),
            TEXT_PRIMARY,
        )
        self._update_counter()

        self.round_summary = self._make_panel(self.container, fg_color=SURFACE_COLOR, corner_radius=12)
        self.round_summary.pack(fill="x", padx=8, pady=(8, 10))

        ctk.CTkLabel(
            self.round_summary,
            text=self.t("series_done_title"),
            font=self._text_font(20, bold=True),
            text_color=TEXT_PRIMARY,
        ).pack(pady=(14, 8))

        ctk.CTkLabel(
            self.round_summary,
            text=self.t("series_done_summary", wins=self.successful_rounds, losses=self.failed_rounds),
            font=self._text_font(15),
            text_color=TEXT_MUTED,
            justify="center",
        ).pack(pady=(0, 10))

        new_text, new_icon = self._button_label(self.t("new_game"), "restart", (18, 16), TEXT_PRIMARY)
        self._make_button(
            self.round_summary,
            new_text,
            command=self.start_interactive_game,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            width=180,
            height=40,
            font_size=15,
            bold=True,
            image=new_icon,
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
            text=self.t("game_over_title", attempts=self.max_open),
            font=self._text_font(18, bold=True),
            text_color="#ffd1d1",
        ).pack(pady=(14, 8))

        ctk.CTkLabel(
            self.round_summary,
            text=self.t("game_over_summary", wins=self.successful_rounds, prisoner=self.prisoner_number),
            font=self._text_font(15),
            text_color=TEXT_MUTED,
            justify="center",
        ).pack(pady=(0, 10))

        new_text, new_icon = self._button_label(self.t("new_game"), "restart", (18, 16), TEXT_PRIMARY)
        self._make_button(
            self.round_summary,
            new_text,
            command=self.start_interactive_game,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            width=180,
            height=40,
            font_size=15,
            bold=True,
            image=new_icon,
        ).pack(pady=(0, 14))

    def run_stats(self) -> None:
        card_limit = len(self.stats_n_cards)
        recent_counts = self.stats_store.recent_prisoner_counts(limit=card_limit)
        for n_value in self.stats_store.available_prisoner_counts(limit=card_limit * 3):
            if n_value not in recent_counts:
                recent_counts.append(n_value)
            if len(recent_counts) >= card_limit:
                break

        for default_n in [100, 10, 25, 50]:
            if default_n not in recent_counts:
                recent_counts.append(default_n)
            if len(recent_counts) >= card_limit:
                break

        self.stats_detail_ns = recent_counts[:card_limit]
        if self.stats_detail_ns:
            self._set_status(self.t("shown_recent_stats"), TEXT_MUTED)
        else:
            self._set_status(self.t("no_saved_games"), TEXT_MUTED)
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

            labels["title"].configure(text=self.t("prisoners_n", count=n_value))
            labels["attempts"].configure(text=self.t("attempts_short", attempts=n_value // 2))
            labels["games"].configure(text=str(n_summary["games"]))
            labels["wins"].configure(text=str(n_summary["wins"]))
            labels["losses"].configure(text=str(n_summary["losses"]))
            labels["saved"].configure(text=str(n_summary["saved_prisoners"]))
            labels["lost"].configure(text=str(n_summary["lost_prisoners"]))
            labels["win_rate"].configure(text=self.t("success_rate", rate=n_summary["win_rate"]))

        if self.stats_fact_label:
            theory_100 = theoretical_optimal_success_rate(100)
            theory_100_random = theoretical_random_success_rate(100)
            self.stats_fact_label.configure(
                text=self.t("interesting_fact", cycle=theory_100, random=theory_100_random)
            )


def main() -> None:
    app = PrisonersApp()
    app.mainloop()


if __name__ == "__main__":
    main()
