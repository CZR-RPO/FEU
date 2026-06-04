from pathlib import Path

from forest_fire.simulator import ForestFireSimulator, Terrain


def test_random_map_respects_percentages() -> None:
    simulator = ForestFireSimulator(
        width=10, height=10, tree_percentage=30, water_percentage=20, seed=42
    )
    cells = [cell for row in simulator.grid for cell in row]
    assert cells.count(Terrain.TREE) == 30
    assert cells.count(Terrain.WATER) == 20
    assert cells.count(Terrain.BARE) == 50


def test_fire_spreads_including_diagonal() -> None:
    simulator = ForestFireSimulator(3, 3, tree_percentage=0, water_percentage=0)
    simulator.grid = [
        [Terrain.TREE, Terrain.BARE, Terrain.BARE],
        [Terrain.BARE, Terrain.TREE, Terrain.BARE],
        [Terrain.BARE, Terrain.BARE, Terrain.TREE],
    ]
    burned = simulator.simulate_fire((0, 0))
    assert burned[0][0] == Terrain.BURNED
    assert burned[1][1] == Terrain.BURNED
    assert burned[2][2] == Terrain.BURNED


def test_water_and_bare_do_not_burn() -> None:
    simulator = ForestFireSimulator(3, 3, tree_percentage=0, water_percentage=0)
    simulator.grid = [
        [Terrain.TREE, Terrain.WATER, Terrain.TREE],
        [Terrain.BARE, Terrain.BARE, Terrain.BARE],
        [Terrain.TREE, Terrain.TREE, Terrain.TREE],
    ]
    burned = simulator.simulate_fire((0, 0))
    assert burned[0][0] == Terrain.BURNED
    assert burned[0][1] == Terrain.WATER
    assert burned[0][2] == Terrain.TREE
    assert burned[2][0] == Terrain.TREE


def test_simulate_fire_steps_contains_iterations() -> None:
    simulator = ForestFireSimulator(3, 3, tree_percentage=0, water_percentage=0)
    simulator.grid = [
        [Terrain.TREE, Terrain.BARE, Terrain.BARE],
        [Terrain.BARE, Terrain.TREE, Terrain.BARE],
        [Terrain.BARE, Terrain.BARE, Terrain.TREE],
    ]
    steps = simulator.simulate_fire_steps((0, 0))
    assert len(steps) == 4
    assert steps[0][0][0] == Terrain.TREE
    assert steps[1][0][0] == Terrain.BURNED
    assert steps[2][1][1] == Terrain.BURNED
    assert steps[3][2][2] == Terrain.BURNED


def test_find_best_tree_to_clear() -> None:
    simulator = ForestFireSimulator(4, 4, tree_percentage=0, water_percentage=0)
    simulator.grid = [
        [Terrain.TREE, Terrain.TREE, Terrain.WATER, Terrain.WATER],
        [Terrain.WATER, Terrain.TREE, Terrain.WATER, Terrain.WATER],
        [Terrain.WATER, Terrain.TREE, Terrain.TREE, Terrain.TREE],
        [Terrain.WATER, Terrain.WATER, Terrain.WATER, Terrain.TREE],
    ]
    best_position, best_burned, reduction = simulator.find_best_tree_to_clear((0, 0))
    assert best_position == (1, 1)
    assert best_burned == 2
    assert reduction == 5


def test_export_html_creates_file(tmp_path: Path) -> None:
    simulator = ForestFireSimulator(2, 2, tree_percentage=50, water_percentage=0, seed=1)
    out_file = tmp_path / "map.html"
    simulator.export_html(out_file)
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "<table>" in content
    assert "Simulation Feu de Foret" in content


def test_export_paginated_html_creates_navigation(tmp_path: Path) -> None:
    simulator = ForestFireSimulator(2, 2, tree_percentage=50, water_percentage=0, seed=1)
    steps = simulator.simulate_fire_steps((0, 0))
    out_file = tmp_path / "map_paginated.html"
    simulator.export_paginated_html(out_file, steps, ignition_start=(0, 0))

    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "btn-prev" in content
    assert "btn-next" in content
    assert "step-select" in content
    assert "const steps =" in content
