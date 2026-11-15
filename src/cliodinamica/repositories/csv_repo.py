"""Exportación a CSV: una serie temporal por simulación más un archivo de metadatos."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cliodinamica.services.simulation import SimulationResult


class CsvRepository:
    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def render(result: SimulationResult) -> str:
        """Devuelve el contenido CSV de la serie temporal como texto."""
        tray = result.trajectory
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerow(["t", *tray.state_names])
        for i, t in enumerate(tray.t):
            writer.writerow([float(t), *(float(tray.y[j, i]) for j in range(len(tray.y)))])
        return buf.getvalue()

    def save(self, result: SimulationResult) -> str:
        csv_path = self.directory / f"{result.run_id}.csv"
        csv_path.write_text(self.render(result), encoding="utf-8")

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
