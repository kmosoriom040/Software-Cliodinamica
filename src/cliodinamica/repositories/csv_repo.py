"""Exportación a CSV: una serie temporal por simulación más un archivo de metadatos."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cliodinamica.services.simulation import SimulationResult


class CsvRepository:
    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, result: SimulationResult) -> str:
        tray = result.trajectory
        csv_path = self.directory / f"{result.run_id}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["t", *tray.state_names])
            for i, t in enumerate(tray.t):
                writer.writerow([float(t), *(float(tray.y[j, i]) for j in range(len(tray.y)))])

        meta = {
            "run_id": result.run_id,
            "model": result.model,
            "params": result.params,
            "t_end": result.t_end,
            "created_at": result.created_at,
        }
        meta_path = self.directory / f"{result.run_id}.meta.json"
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(csv_path)
