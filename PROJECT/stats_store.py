import json
import sqlite3
from pathlib import Path
from typing import Dict, Optional


class StatsStore:
    def __init__(self, db_path: Path, legacy_json_path: Optional[Path] = None) -> None:
        self.db_path = db_path
        self.legacy_json_path = legacy_json_path
        self._ensure_schema()
        self._migrate_legacy_json_if_needed()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS stats_total (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    total_games INTEGER NOT NULL DEFAULT 0,
                    wins INTEGER NOT NULL DEFAULT 0,
                    losses INTEGER NOT NULL DEFAULT 0,
                    saved_prisoners INTEGER NOT NULL DEFAULT 0,
                    lost_prisoners INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS stats_by_n (
                    total_prisoners INTEGER PRIMARY KEY,
                    games INTEGER NOT NULL DEFAULT 0,
                    wins INTEGER NOT NULL DEFAULT 0,
                    losses INTEGER NOT NULL DEFAULT 0,
                    saved_prisoners INTEGER NOT NULL DEFAULT 0,
                    lost_prisoners INTEGER NOT NULL DEFAULT 0
                );
                """
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO stats_total (
                    id, total_games, wins, losses, saved_prisoners, lost_prisoners
                ) VALUES (1, 0, 0, 0, 0, 0)
                """
            )

    def _migrate_legacy_json_if_needed(self) -> None:
        if self.legacy_json_path is None or not self.legacy_json_path.exists():
            return

        with self._connect() as conn:
            row = conn.execute("SELECT total_games FROM stats_total WHERE id = 1").fetchone()
            current_games = int(row["total_games"]) if row else 0
            if current_games > 0:
                return

        try:
            payload = json.loads(self.legacy_json_path.read_text(encoding="utf-8"))
        except Exception:
            return

        if not isinstance(payload, dict):
            return

        total_games = int(payload.get("total_games", 0))
        wins = int(payload.get("wins", 0))
        losses = int(payload.get("losses", 0))
        saved = int(payload.get("saved_prisoners", 0))
        lost = int(payload.get("lost_prisoners", 0))
        by_n = payload.get("by_n", {})
        if not isinstance(by_n, dict):
            by_n = {}

        with self._connect() as conn:
            conn.execute("DELETE FROM stats_by_n")
            conn.execute(
                """
                UPDATE stats_total
                SET total_games = ?, wins = ?, losses = ?,
                    saved_prisoners = ?, lost_prisoners = ?
                WHERE id = 1
                """,
                (
                    max(0, total_games),
                    max(0, wins),
                    max(0, losses),
                    max(0, saved),
                    max(0, lost),
                ),
            )

            for n_key, stats in by_n.items():
                if not isinstance(stats, dict):
                    continue
                try:
                    n_value = int(n_key)
                except (TypeError, ValueError):
                    continue

                conn.execute(
                    """
                    INSERT INTO stats_by_n (
                        total_prisoners, games, wins, losses, saved_prisoners, lost_prisoners
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        n_value,
                        max(0, int(stats.get("games", 0))),
                        max(0, int(stats.get("wins", 0))),
                        max(0, int(stats.get("losses", 0))),
                        max(0, int(stats.get("saved_prisoners", 0))),
                        max(0, int(stats.get("lost_prisoners", 0))),
                    ),
                )

    def save(self) -> None:
        return

    def record_game(self, won: bool, total_prisoners: int, saved_prisoners: int) -> None:
        saved = max(0, min(int(saved_prisoners), int(total_prisoners)))
        lost = max(0, total_prisoners - saved)

        with self._connect() as conn:
            conn.execute(
                """
                UPDATE stats_total
                SET total_games = total_games + 1,
                    wins = wins + ?,
                    losses = losses + ?,
                    saved_prisoners = saved_prisoners + ?,
                    lost_prisoners = lost_prisoners + ?
                WHERE id = 1
                """,
                (int(won), int(not won), saved, lost),
            )
            conn.execute(
                """
                INSERT INTO stats_by_n (
                    total_prisoners, games, wins, losses, saved_prisoners, lost_prisoners
                ) VALUES (?, 1, ?, ?, ?, ?)
                ON CONFLICT(total_prisoners) DO UPDATE SET
                    games = games + 1,
                    wins = wins + excluded.wins,
                    losses = losses + excluded.losses,
                    saved_prisoners = saved_prisoners + excluded.saved_prisoners,
                    lost_prisoners = lost_prisoners + excluded.lost_prisoners
                """,
                (total_prisoners, int(won), int(not won), saved, lost),
            )

    def total_summary(self) -> Dict[str, float]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT total_games, wins, losses, saved_prisoners, lost_prisoners
                FROM stats_total
                WHERE id = 1
                """
            ).fetchone()

        total_games = int(row["total_games"]) if row else 0
        wins = int(row["wins"]) if row else 0
        losses = int(row["losses"]) if row else 0
        saved = int(row["saved_prisoners"]) if row else 0
        lost = int(row["lost_prisoners"]) if row else 0
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
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT games, wins, losses, saved_prisoners, lost_prisoners
                FROM stats_by_n
                WHERE total_prisoners = ?
                """,
                (total_prisoners,),
            ).fetchone()

        games = int(row["games"]) if row else 0
        wins = int(row["wins"]) if row else 0
        losses = int(row["losses"]) if row else 0
        saved = int(row["saved_prisoners"]) if row else 0
        lost = int(row["lost_prisoners"]) if row else 0
        win_rate = (wins / games * 100) if games else 0.0

        return {
            "games": games,
            "wins": wins,
            "losses": losses,
            "saved_prisoners": saved,
            "lost_prisoners": lost,
            "win_rate": win_rate,
        }
