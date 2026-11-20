"""Prove every verify.py check fires on a deliberately broken part (and passes on a good one).

Run:  .venv/bin/python -m pytest -q tests/test_verify.py
Test geometry sizes are arbitrary test fixtures, not design values.
"""
import tempfile
from pathlib import Path

import numpy as np
import trimesh

import verify
from parts.shop import const

TUBE_ID = const("airframe.loc_38mm_paper.id_measured_mm")
TUBE_OD = const("airframe.loc_38mm_paper.od_nominal_mm")
RHO = const("material.petg.density_g_cm3") / 1000.0


def good_plug(length=40.0):
    """Shoulder-like plug at snug-slip fit inside the tube ID."""
    d = TUBE_ID - 2 * const("fits_in_tube.snug_slip_mm_per_side")
    m = trimesh.creation.cylinder(radius=d / 2, height=length, sections=128)
    m.apply_translation([0, 0, length / 2])
    return m


def tube_wall(length=40.0):
    outer = trimesh.creation.cylinder(radius=TUBE_OD / 2, height=length, sections=128)
    inner = trimesh.creation.cylinder(radius=TUBE_ID / 2, height=length + 2, sections=128)
    t = trimesh.boolean.difference([outer, inner], engine="manifold")
    t.apply_translation([0, 0, length / 2])
    return t


def solid_mass(m):
    return m.volume * RHO


def test_good_part_passes_all_auto_checks():
    m = good_plug()
    with tempfile.TemporaryDirectory() as d:
        checks = verify.run(m, solid_mass(m), {"tube": tube_wall()}, Path(d), "good")
    assert all(c.passed for c in checks), verify.summary(checks)


def test_check1_fires_on_open_mesh():
    m = good_plug()
    m.update_faces(np.arange(len(m.faces)) > 3)  # delete faces -> hole
    assert not verify.check_mesh(m).passed


def test_check1_fires_on_floating_body():
    a = trimesh.creation.box([10, 10, 10])
    b = trimesh.creation.box([10, 10, 10]); b.apply_translation([30, 0, 0])
    assert not verify.check_mesh(trimesh.util.concatenate([a, b])).passed


def test_check2_fires_on_wrong_mass():
    m = good_plug()
    assert not verify.check_mass(m, solid_mass(m) * 3).passed   # unreachable even at 100 % infill
    assert not verify.check_mass(m, solid_mass(m) * 0.1).passed  # below the 0 % infill shell mass


def test_check3_fires_on_interference():
    fat = trimesh.creation.cylinder(radius=(TUBE_ID / 2) + 0.5, height=40, sections=128)  # 0.5 mm into the wall
    fat.apply_translation([0, 0, 20])
    c = verify.check_mating(fat, {"tube": tube_wall()})
    assert not c.passed and c.data["interference_mm3"]["tube"] > 1.0


def test_check3_fires_when_no_mating_declared():
    assert not verify.check_mating(good_plug(), {}).passed


def test_check4_writes_three_pngs():
    with tempfile.TemporaryDirectory() as d:
        c = verify.render(good_plug(), Path(d), "r")
        assert c.passed and len(list(Path(d).glob("r_*.png"))) == 3


def test_check5_fires_on_too_tall():
    tall = trimesh.creation.cylinder(radius=10, height=const("printer.bambu_p1s.max_z_mm") + 10)
    assert not verify.check_build_volume(tall).passed
