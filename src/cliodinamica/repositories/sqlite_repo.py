"""Almacenamiento en una base SQLite local (solo biblioteca estándar)."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from cliodinamica.core import Trajectory

if TYPE_CHECKING:
    from cliodinamica.services.simulation import SimulationResult

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    model TEXT NOT NULL,
    params TEXT NOT NULL,
    t_end REAL NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS series (
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    step INTEGER NOT NULL,
    t REAL NOT NULL,
    state TEXT NOT NULL,
    value REAL NOT NULL,
    PRIMARY KEY (run_id, step, state)
);
"""


class SqliteRepository:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as con:
            con.executescript(_SCHEMA)

    def save(self, result: SimulationResult) -> str:
        tray = result.trajectory
        rows = [
            (result.run_id, i, float(t), name, float(tray.y[j, i]))
            for i, t in enumerate(tray.t)
            for j, name in enumerate(tray.state_names)
        ]
        with closing(sqlite3.connect(self.path)) as con, con:
            con.execute(
                "INSERT INTO runs VALUES (?, ?, ?, ?, ?)",
                (
                    result.run_id,
                    result.model,
                    json.dumps(result.params),
                    result.t_end,
                    result.created_at,
                ),
            )
            con.executemany("INSERT INTO series VALUES (?, ?, ?, ?, ?)", rows)
        return result.run_id

    def list_runs(self) -> list[dict]:
        with closing(sqlite3.connect(self.path)) as con:
            cur = con.execute(
                "SELECT run_id, model, params, t_end, created_at FROM runs ORDER BY created_at"
            )
            return [
                {"run_id": r[0], "model": r[1], "params": json.loads(r[2]),
                 "t_end": r[3], "created_at": r[4]}
                for r in cur.fetchall()
            ]

    def load_trajectory(self, run_id: str) -> Trajectory:
        with closing(sqlite3.connect(self.path)) as con:
            states = [
                r[0]
                for r in con.execute(
                    "SELECT state FROM series WHERE run_id = ? AND step = 0 ORDER BY rowid",
                    (run_id,),
                )
            ]
            if not states:
                raise KeyError(f"No existe la simulación {run_id!r}")
            t = np.array(
                [r[0] for r in con.execute(
                    "SELECT t FROM series WHERE run_id = ? AND state = ? ORDER BY step",
                    (run_id, states[0]),
                )]
            )
            y = np.array(
                [
                    [r[0] for r in con.execute(
                        "SELECT value FROM series WHERE run_id = ? AND state = ? ORDER BY step",
                        (run_id, s),
                    )]
                    for s in states
                ]
            )
        return Trajectory(t=t, y=y, state_names=tuple(states))
