import csv
import json

import numpy as np
import pytest

from cliodinamica.repositories import CsvRepository, SqliteRepository
from cliodinamica.services import SimulationService


def test_run_con_parametros_sobrescritos():
    res = SimulationService().run(params={"lam": 0.5}, t_end=50, n_points=51)
    assert res.params["lam"] == 0.5
    assert res.trajectory.y.shape == (4, 51)


def test_parametro_desconocido():
    with pytest.raises(ValueError, match="desconocidos"):
        SimulationService().run(params={"inexistente": 1.0})


def test_guardar_sin_repositorio():
    svc = SimulationService()
    with pytest.raises(RuntimeError):
        svc.save(svc.run(t_end=10, n_points=11))


def test_exportacion_csv(tmp_path):
    svc = SimulationService(CsvRepository(tmp_path))
    res = svc.run(t_end=20, n_points=21, save=True)
    with (tmp_path / f"{res.run_id}.csv").open(encoding="utf-8") as f:
        filas = list(csv.reader(f))
    assert filas[0] == ["t", "N", "R", "G", "S"]
    assert len(filas) == 22
    assert float(filas[-1][1]) == pytest.approx(res.trajectory.series("N")[-1])
    meta = json.loads((tmp_path / f"{res.run_id}.meta.json").read_text(encoding="utf-8"))
    assert meta["model"] == "cliodinamica"


def test_sqlite_ida_y_vuelta(tmp_path):
    repo = SqliteRepository(tmp_path / "sim.sqlite")
    svc = SimulationService(repo)
    res = svc.run(t_end=30, n_points=31, save=True)
    tray = repo.load_trajectory(res.run_id)
    assert tray.state_names == res.trajectory.state_names
    assert np.allclose(tray.y, res.trajectory.y)
    assert [r["run_id"] for r in repo.list_runs()] == [res.run_id]


def test_sqlite_simulacion_inexistente(tmp_path):
    with pytest.raises(KeyError):
        SqliteRepository(tmp_path / "sim.sqlite").load_trajectory("nada")
