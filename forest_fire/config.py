from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

Position = tuple[int, int]


@dataclass(frozen=True)
class SimulationConfig:
    width: int = 20
    height: int = 12
    tree_percentage: float = 55
    water_percentage: float = 10
    seed: int = 11
    requested_start: Position = (5, 9)
    water_protection: bool = True
    paginated_html_path: str = "carte_brulee_paginee.html"


def validate_config_input(
    width_str: str,
    height_str: str,
    tree_pct_str: str,
    water_pct_str: str,
    seed_str: str,
    start_row_str: str,
    start_col_str: str,
    water_protection: bool,
) -> tuple[Optional[SimulationConfig], str]:
    """Parse and validate raw string inputs. Returns (config, "") or (None, error_message)."""
    try:
        width = int(width_str)
        height = int(height_str)
        tree_pct = float(tree_pct_str)
        water_pct = float(water_pct_str)
        seed = int(seed_str)
        start_row = int(start_row_str)
        start_col = int(start_col_str)
    except ValueError:
        return None, "Toutes les valeurs doivent être numériques."

    if width <= 0 or height <= 0:
        return None, "Largeur et hauteur doivent être > 0."
    if not (0 <= tree_pct <= 100 and 0 <= water_pct <= 100):
        return None, "Les pourcentages doivent être entre 0 et 100."
    if tree_pct + water_pct > 100:
        return None, "% arbres + % eau ne peut pas dépasser 100."

    return SimulationConfig(
        width=width,
        height=height,
        tree_percentage=tree_pct,
        water_percentage=water_pct,
        seed=seed,
        requested_start=(start_row, start_col),
        water_protection=water_protection,
    ), ""
