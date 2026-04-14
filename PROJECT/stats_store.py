import json
from pathlib import Path
from typing import Dict


class StatsStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = self._load()

    def _empty_payload(self) -> Dict[str, object]:
        return {
            "total_games": 0,
            "wins": 0,
            "losses": 0,
            "saved_prisoners": 0,
            "lost_prisoners": 0,
            "by_n": {},
        }

    def _load(self) -> Dict[str, object]:
        if not self.path.exists():
            return self._empty_payload()
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                payload = self._empty_payload()
                payload.update(loaded)
                if not isinstance(payload.get("by_n"), dict):
                    payload["by_n"] = {}
                return payload
        except Exception:
            pass
        return self._empty_payload()

    def save(self) -> None:
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def record_game(self, won: bool, total_prisoners: int, saved_prisoners: int) -> None:
        saved = max(0, min(saved_prisoners, total_prisoners))
        lost = max(0, total_prisoners - saved)

        self.data["total_games"] = int(self.data.get("total_games", 0)) + 1
        self.data["wins"] = int(self.data.get("wins", 0)) + int(won)
        self.data["losses"] = int(self.data.get("losses", 0)) + int(not won)
        self.data["saved_prisoners"] = int(self.data.get("saved_prisoners", 0)) + saved
        self.data["lost_prisoners"] = int(self.data.get("lost_prisoners", 0)) + lost

        by_n = self.data.setdefault("by_n", {})
        if not isinstance(by_n, dict):
            by_n = {}
            self.data["by_n"] = by_n

        n_key = str(total_prisoners)
        n_data = by_n.get(n_key)
        if not isinstance(n_data, dict):
            n_data = {
                "games": 0,
                "wins": 0,
                "losses": 0,
                "saved_prisoners": 0,
                "lost_prisoners": 0,
            }
            by_n[n_key] = n_data

        n_data["games"] = int(n_data.get("games", 0)) + 1
        n_data["wins"] = int(n_data.get("wins", 0)) + int(won)
        n_data["losses"] = int(n_data.get("losses", 0)) + int(not won)
        n_data["saved_prisoners"] = int(n_data.get("saved_prisoners", 0)) + saved
        n_data["lost_prisoners"] = int(n_data.get("lost_prisoners", 0)) + lost

    def total_summary(self) -> Dict[str, float]:
        total_games = int(self.data.get("total_games", 0))
        wins = int(self.data.get("wins", 0))
        losses = int(self.data.get("losses", 0))
        saved = int(self.data.get("saved_prisoners", 0))
        lost = int(self.data.get("lost_prisoners", 0))
        win_rate = (wins / total_games * 100) if total_games else 0.0
        return {
            "games": total_games,
            "wins": wins,
            "losses": losses,
            "saved_prisoners": saved,
            "lost_prisoners": lost,
            "win_rate": win_rate,
        }

    def summary_for_n(self, total_prisoners: int) -> Dict[str, float]:
        by_n = self.data.get("by_n", {})
        if not isinstance(by_n, dict):
            by_n = {}
        stats = by_n.get(str(total_prisoners), {})
        if not isinstance(stats, dict):
            stats = {}

        games = int(stats.get("games", 0))
        wins = int(stats.get("wins", 0))
        losses = int(stats.get("losses", 0))
        saved = int(stats.get("saved_prisoners", 0))
        lost = int(stats.get("lost_prisoners", 0))
        win_rate = (wins / games * 100) if games else 0.0
        return {
            "games": games,
            "wins": wins,
            "losses": losses,
            "saved_prisoners": saved,
            "lost_prisoners": lost,
            "win_rate": win_rate,
        }
