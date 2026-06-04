from __future__ import annotations

from collections import deque
import json
from pathlib import Path
import random
from typing import Optional

Grid = list[list[str]]
Position = tuple[int, int]


class Terrain:
    BARE = "N"
    TREE = "A"
    WATER = "E"
    BURNED = "B"


class ForestFireSimulator:
    def __init__(
        self,
        width: int,
        height: int,
        tree_percentage: float,
        water_percentage: float = 10.0,
        seed: Optional[int] = None,
        water_protection: bool = True,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be strictly positive")
        if not (0 <= tree_percentage <= 100):
            raise ValueError("tree_percentage must be between 0 and 100")
        if not (0 <= water_percentage <= 100):
            raise ValueError("water_percentage must be between 0 and 100")
        if tree_percentage + water_percentage > 100:
            raise ValueError("tree_percentage + water_percentage must be <= 100")

        self.width = width
        self.height = height
        self.tree_percentage = tree_percentage
        self.water_percentage = water_percentage
        self.water_protection = water_protection
        self._random = random.Random(seed)
        self.grid: Grid = self.generate_random_map()

    def generate_random_map(self) -> Grid:
        total = self.width * self.height
        tree_count = round(total * self.tree_percentage / 100)
        water_count = round(total * self.water_percentage / 100)
        bare_count = total - tree_count - water_count

        cells = (
            [Terrain.TREE] * tree_count
            + [Terrain.WATER] * water_count
            + [Terrain.BARE] * bare_count
        )
        self._random.shuffle(cells)
        self.grid = [
            cells[row * self.width : (row + 1) * self.width] for row in range(self.height)
        ]
        return self.copy_grid(self.grid)

    @staticmethod
    def copy_grid(grid: Grid) -> Grid:
        return [row[:] for row in grid]

    def _in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.height and 0 <= col < self.width

    def _neighbors_8(self, row: int, col: int) -> list[Position]:
        neighbors: list[Position] = []
        for d_row in (-1, 0, 1):
            for d_col in (-1, 0, 1):
                if d_row == 0 and d_col == 0:
                    continue
                n_row = row + d_row
                n_col = col + d_col
                if self._in_bounds(n_row, n_col):
                    neighbors.append((n_row, n_col))
        return neighbors

    def _is_adjacent_to_water(self, row: int, col: int, grid: Grid) -> bool:
        return any(grid[n_row][n_col] == Terrain.WATER for n_row, n_col in self._neighbors_8(row, col))

    def simulate_fire(self, start: Position, grid: Optional[Grid] = None) -> Grid:
        steps = self.simulate_fire_steps(start=start, grid=grid)
        return steps[-1]

    def simulate_fire_steps(self, start: Position, grid: Optional[Grid] = None) -> list[Grid]:
        source = grid if grid is not None else self.grid
        result = self.copy_grid(source)
        start_row, start_col = start

        if not self._in_bounds(start_row, start_col):
            raise ValueError("start position is outside map bounds")

        steps = [self.copy_grid(result)]
        if source[start_row][start_col] != Terrain.TREE:
            return steps

        frontier: deque[Position] = deque([(start_row, start_col)])
        result[start_row][start_col] = Terrain.BURNED
        steps.append(self.copy_grid(result))

        while frontier:
            next_frontier: deque[Position] = deque()
            while frontier:
                row, col = frontier.popleft()
                for n_row, n_col in self._neighbors_8(row, col):
                    if (
                        source[n_row][n_col] == Terrain.TREE
                        and result[n_row][n_col] != Terrain.BURNED
                        and not (
                            self.water_protection
                            and self._is_adjacent_to_water(n_row, n_col, source)
                        )
                    ):
                        result[n_row][n_col] = Terrain.BURNED
                        next_frontier.append((n_row, n_col))

            if next_frontier:
                steps.append(self.copy_grid(result))
            frontier = next_frontier

        return steps

    def burned_cells_count(self, start: Position, grid: Optional[Grid] = None) -> int:
        burned_map = self.simulate_fire(start=start, grid=grid)
        return sum(cell == Terrain.BURNED for row in burned_map for cell in row)

    def find_best_tree_to_clear(
        self, start: Position
    ) -> tuple[Optional[Position], int, int]:
        baseline = self.burned_cells_count(start=start, grid=self.grid)
        start_row, start_col = start

        best_position: Optional[Position] = None
        best_burned = baseline

        for row in range(self.height):
            for col in range(self.width):
                if (row, col) == (start_row, start_col):
                    continue
                if self.grid[row][col] != Terrain.TREE:
                    continue
                candidate = self.copy_grid(self.grid)
                candidate[row][col] = Terrain.BARE
                burned = self.burned_cells_count(start=start, grid=candidate)
                if burned < best_burned:
                    best_burned = burned
                    best_position = (row, col)

        reduction = baseline - best_burned
        return best_position, best_burned, reduction

    def export_html(self, path: str | Path, grid: Optional[Grid] = None) -> None:
        map_to_export = grid if grid is not None else self.grid
        destination = Path(path)

        legend = {
            Terrain.BARE: ("Terrain nu", "#d9c5a0"),
            Terrain.TREE: ("Arbre", "#2d8a3d"),
            Terrain.WATER: ("Eau", "#4a90e2"),
            Terrain.BURNED: ("Brule", "#3b3b3b"),
        }

        rows_html = []
        for row in map_to_export:
            cells = []
            for cell in row:
                label, color = legend[cell]
                cells.append(
                    f'<td class="cell" style="background:{color}" title="{label}">{cell}</td>'
                )
            rows_html.append(f"<tr>{''.join(cells)}</tr>")

        html = f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Simulation Feu de Foret</title>
  <style>
    body {{
      font-family: "Segoe UI", Tahoma, sans-serif;
      background: #f5f5f0;
      color: #1f1f1f;
      margin: 2rem;
    }}
    table {{ border-collapse: collapse; margin-top: 1rem; }}
    .cell {{
      width: 28px;
      height: 28px;
      text-align: center;
      border: 1px solid #ffffff;
      font-size: 0.8rem;
      font-weight: 600;
      color: #ffffff;
    }}
  </style>
</head>
<body>
  <h1>Simulation Feu de Foret</h1>
  <p>A: arbre, N: terrain nu, E: eau, B: brule</p>
  <table>
    {''.join(rows_html)}
  </table>
</body>
</html>
"""

        destination.write_text(html, encoding="utf-8")

    def export_paginated_html(
        self,
        path: str | Path,
        steps: list[Grid],
        ignition_start: Optional[Position] = None,
    ) -> None:
        if not steps:
            raise ValueError("steps must contain at least one grid")

        destination = Path(path)
        steps_json = json.dumps(steps)
        ignition = str(ignition_start) if ignition_start is not None else "N/A"

        html = f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Simulation Feu de Foret - Pagination</title>
  <style>
    body {{
      font-family: "Segoe UI", Tahoma, sans-serif;
      background: #f5f5f0;
      color: #1f1f1f;
      margin: 2rem;
    }}
    .controls {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin: 1rem 0;
      flex-wrap: wrap;
    }}
    button, select {{
      font: inherit;
      padding: 0.35rem 0.6rem;
    }}
    table {{ border-collapse: collapse; margin-top: 0.5rem; }}
    .cell {{
      width: 28px;
      height: 28px;
      text-align: center;
      border: 1px solid #ffffff;
      font-size: 0.8rem;
      font-weight: 600;
      color: #ffffff;
    }}
  </style>
</head>
<body>
  <h1>Simulation Feu de Foret - Iterations</h1>
  <p id="status"></p>
  <div class="controls">
    <button id="btn-prev" type="button">Precedent</button>
    <button id="btn-next" type="button">Suivant</button>
    <label for="step-select">Iteration:</label>
    <select id="step-select"></select>
  </div>
  <table id="grid"></table>

  <script>
    const steps = {steps_json};
    const colors = {{
      "N": "#d9c5a0",
      "A": "#2d8a3d",
      "E": "#4a90e2",
      "B": "#3b3b3b"
    }};
    const ignition = "{ignition}";
    const total = steps.length - 1;
    let current = 0;

    const status = document.getElementById("status");
    const grid = document.getElementById("grid");
    const prevBtn = document.getElementById("btn-prev");
    const nextBtn = document.getElementById("btn-next");
    const stepSelect = document.getElementById("step-select");

    for (let i = 0; i < steps.length; i += 1) {{
      const option = document.createElement("option");
      option.value = String(i);
      option.textContent = String(i);
      stepSelect.appendChild(option);
    }}

    function burnedCount(step) {{
      let count = 0;
      for (const row of step) {{
        for (const cell of row) {{
          if (cell === "B") count += 1;
        }}
      }}
      return count;
    }}

    function render(index) {{
      current = index;
      grid.innerHTML = "";
      const step = steps[index];
      for (const row of step) {{
        const tr = document.createElement("tr");
        for (const cell of row) {{
          const td = document.createElement("td");
          td.className = "cell";
          td.textContent = cell;
          td.style.background = colors[cell];
          tr.appendChild(td);
        }}
        grid.appendChild(tr);
      }}

      status.textContent =
        `Iteration ${{index}}/${{total}} | Cases brulees: ${{burnedCount(step)}} | ` +
        `Depart: ${{ignition}} | A=Arbre N=Nu E=Eau B=Brule`;
      stepSelect.value = String(index);
      prevBtn.disabled = index === 0;
      nextBtn.disabled = index === steps.length - 1;
    }}

    prevBtn.addEventListener("click", () => {{
      if (current > 0) render(current - 1);
    }});

    nextBtn.addEventListener("click", () => {{
      if (current < steps.length - 1) render(current + 1);
    }});

    stepSelect.addEventListener("change", () => {{
      render(Number(stepSelect.value));
    }});

    window.addEventListener("keydown", (event) => {{
      if (event.key === "ArrowLeft" && current > 0) render(current - 1);
      if (event.key === "ArrowRight" && current < steps.length - 1) render(current + 1);
    }});

    render(0);
  </script>
</body>
</html>
"""

        destination.write_text(html, encoding="utf-8")
