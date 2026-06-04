from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

from forest_fire import ForestFireSimulator, Terrain

Grid = list[list[str]]
Position = tuple[int, int]


@dataclass(frozen=True)
class SimulationConfig:
    width: int = 20 #largeur
    height: int = 12 #hauteur
    tree_percentage: float = 55 #chance d'avoir une case arbre
    water_percentage: float = 10 #chance d'avoir une case eau 
    seed: int = 11 #seed de génération d'aléatoire des cases
    requested_start: Position = (5, 9) #feu de départ
    paginated_html_path: str = "carte_brulee_paginee.html"


class FireSimulationApp:
    CELL_SIZE = 28
    PADDING = 1

    COLORS = {
        Terrain.BARE: "#d9c5a0",
        Terrain.TREE: "#2d8a3d",
        Terrain.WATER: "#4a90e2",
        Terrain.BURNED: "#3b3b3b",
    }

    LABELS = {
        Terrain.BARE: "Terrain nu",
        Terrain.TREE: "Arbre",
        Terrain.WATER: "Eau",
        Terrain.BURNED: "Brule",
    }

    def __init__(
        self,
        simulator: ForestFireSimulator,
        steps: list[Grid],
        ignition_start: Position,
    ) -> None:
        self.simulator = simulator
        self.steps = steps
        self.ignition_start = ignition_start
        self.current_step = 0

        self.root = tk.Tk()
        self.root.title("Simulation Feu de Foret - Iterations")
        self.root.configure(background="#f4f3ee")

        self.status_var = tk.StringVar()
        self.step_var = tk.StringVar(value="0")

        self._build_layout()
        self._render_step(0)

        self.root.bind("<Left>", lambda _event: self.previous_step())
        self.root.bind("<Right>", lambda _event: self.next_step())

    def _build_layout(self) -> None:
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill="x")

        title = ttk.Label(top, text="Simulation Feu de Foret", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, columnspan=4, sticky="w")

        self.status_label = ttk.Label(top, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, columnspan=4, sticky="w", pady=(6, 0))

        controls = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        controls.pack(fill="x")

        self.prev_button = ttk.Button(controls, text="Precedent", command=self.previous_step)
        self.prev_button.grid(row=0, column=0, padx=(0, 8))

        self.next_button = ttk.Button(controls, text="Suivant", command=self.next_step)
        self.next_button.grid(row=0, column=1, padx=(0, 14))

        ttk.Label(controls, text="Iteration:").grid(row=0, column=2, padx=(0, 6))
        self.step_combo = ttk.Combobox(
            controls,
            textvariable=self.step_var,
            values=[str(i) for i in range(len(self.steps))],
            width=8,
            state="readonly",
        )
        self.step_combo.grid(row=0, column=3)
        self.step_combo.bind("<<ComboboxSelected>>", self.on_step_selected)

        width = self.simulator.width * self.CELL_SIZE
        height = self.simulator.height * self.CELL_SIZE
        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            highlightthickness=0,
            bg="#f4f3ee",
        )
        self.canvas.pack(padx=12, pady=(0, 12))

    def _draw_grid(self, grid: Grid) -> None:
        self.canvas.delete("all")
        for row_idx, row in enumerate(grid):
            for col_idx, cell in enumerate(row):
                x1 = col_idx * self.CELL_SIZE + self.PADDING
                y1 = row_idx * self.CELL_SIZE + self.PADDING
                x2 = (col_idx + 1) * self.CELL_SIZE - self.PADDING
                y2 = (row_idx + 1) * self.CELL_SIZE - self.PADDING
                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=self.COLORS[cell],
                    outline="#ffffff",
                )
                self.canvas.create_text(
                    (x1 + x2) // 2,
                    (y1 + y2) // 2,
                    text=cell,
                    fill="#ffffff",
                    font=("Segoe UI", 9, "bold"),
                )

    def _update_status(self, step_index: int, grid: Grid) -> None:
        total = len(self.steps) - 1
        burned_count = sum(cell == Terrain.BURNED for row in grid for cell in row)
        self.status_var.set(
            f"Iteration {step_index}/{total} | Cases brulees: {burned_count} | "
            f"Depart: {self.ignition_start} | A=Arbre N=Nu E=Eau B=Brule"
        )

    def _update_navigation(self, step_index: int) -> None:
        self.step_var.set(str(step_index))
        self.prev_button.configure(state="normal" if step_index > 0 else "disabled")
        self.next_button.configure(state="normal" if step_index < len(self.steps) - 1 else "disabled")

    def _render_step(self, step_index: int) -> None:
        self.current_step = step_index
        grid = self.steps[step_index]
        self._draw_grid(grid)
        self._update_status(step_index, grid)
        self._update_navigation(step_index)

    def on_step_selected(self, _event: object) -> None:
        selected_index = int(self.step_var.get())
        self._render_step(selected_index)

    def previous_step(self) -> None:
        if self.current_step > 0:
            self._render_step(self.current_step - 1)

    def next_step(self) -> None:
        if self.current_step < len(self.steps) - 1:
            self._render_step(self.current_step + 1)

    def run(self) -> None:
        self.root.mainloop()


def build_simulation(config: SimulationConfig) -> tuple[ForestFireSimulator, Position, list[Grid]]:
    sim = ForestFireSimulator(
        width=config.width,
        height=config.height,
        tree_percentage=config.tree_percentage,
        water_percentage=config.water_percentage,
        seed=config.seed,
    )
    start = find_ignition_start(sim, config.requested_start)
    steps = sim.simulate_fire_steps(start)
    return sim, start, steps


def main() -> None:
    config = SimulationConfig()
    simulator, ignition_start, steps = build_simulation(config)
    simulator.export_paginated_html(config.paginated_html_path, steps, ignition_start)

    app = FireSimulationApp(simulator=simulator, steps=steps, ignition_start=ignition_start)
    app.run()


def find_ignition_start(
    simulator: ForestFireSimulator, requested_start: Position
) -> Position:
    row, col = requested_start
    if 0 <= row < simulator.height and 0 <= col < simulator.width:
        if simulator.grid[row][col] == Terrain.TREE:
            return requested_start

    for r in range(simulator.height):
        for c in range(simulator.width):
            if simulator.grid[r][c] == Terrain.TREE:
                return (r, c)
    raise ValueError("La carte ne contient aucun arbre pour demarrer un incendie.")


if __name__ == "__main__":
    main()
