# Cas pratique - simulateur de feux de forets

Ce depot contient une implementation Python du cas pratique:
- generation aleatoire d'une carte (`N` terrain nu, `A` arbre, `E` eau),
- simulation de propagation d'incendie (voisinage 8 directions, diagonales incluses),
- recherche de la meilleure case d'arbre a deboiser pour limiter les degats,
- export HTML du resultat.

## Installation

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## Executer les tests

```bash
pytest -q
```

## Exemple d'utilisation

```python
from forest_fire import ForestFireSimulator

sim = ForestFireSimulator(width=20, height=12, tree_percentage=55, water_percentage=10, seed=7)
start = (5, 9)

burned_map = sim.simulate_fire(start)
best_cell, burned_after_clear, reduction = sim.find_best_tree_to_clear(start)

sim.export_html("carte_initiale.html")
sim.export_html("carte_brulee.html", grid=burned_map)
```

## CI Github Actions

Le workflow [`.github/workflows/tests.yml`](.github/workflows/tests.yml) lance `pytest` a chaque:
- `push`
- `pull_request`

## Organisation Git conseillee

Pour coller au sujet, vous pouvez travailler par branches:
1. `feature/map-generation`
2. `feature/fire-simulation`
3. `feature/optimization`
4. `feature/html-export`
5. `chore/tests-and-ci`

Puis ouvrir une Pull Request par lot coherent avec des commits explicites.

## Hypothese

La methode d'optimisation n'autorise pas le deboisement de la case de depart de l'incendie, pour eviter une solution triviale.
