from forest_fire.config import SimulationConfig, validate_config_input

_D = SimulationConfig()


def _call(**overrides: object) -> tuple:
    """Appelle validate_config_input avec les valeurs par défaut, surchargées par overrides."""
    fields: dict = {
        "width_str": str(_D.width),
        "height_str": str(_D.height),
        "tree_pct_str": str(_D.tree_percentage),
        "water_pct_str": str(_D.water_percentage),
        "seed_str": str(_D.seed),
        "start_row_str": str(_D.requested_start[0]),
        "start_col_str": str(_D.requested_start[1]),
        "water_protection": _D.water_protection,
    }
    fields.update(overrides)
    return validate_config_input(**fields)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Entrées valides
# ---------------------------------------------------------------------------

def test_valid_defaults_produce_config() -> None:
    config, error = _call()
    assert config is not None and error == ""
    assert config.width == _D.width
    assert config.height == _D.height
    assert config.tree_percentage == _D.tree_percentage
    assert config.water_percentage == _D.water_percentage
    assert config.seed == _D.seed
    assert config.requested_start == _D.requested_start
    assert config.water_protection == _D.water_protection


def test_valid_custom_values() -> None:
    config, error = _call(
        width_str="10", height_str="8",
        tree_pct_str="30", water_pct_str="20",
        seed_str="42", start_row_str="2", start_col_str="3",
        water_protection=False,
    )
    assert config is not None and error == ""
    assert config.width == 10
    assert config.height == 8
    assert config.tree_percentage == 30.0
    assert config.water_percentage == 20.0
    assert config.seed == 42
    assert config.requested_start == (2, 3)
    assert config.water_protection is False


def test_water_protection_true_propagated() -> None:
    config, _ = _call(water_protection=True)
    assert config is not None and config.water_protection is True


def test_water_protection_false_propagated() -> None:
    config, _ = _call(water_protection=False)
    assert config is not None and config.water_protection is False


def test_float_percentages_accepted() -> None:
    config, error = _call(tree_pct_str="33.5", water_pct_str="10.5")
    assert config is not None and error == ""


def test_zero_percentages_accepted() -> None:
    config, error = _call(tree_pct_str="0", water_pct_str="0")
    assert config is not None and error == ""


def test_percentage_sum_exactly_100_accepted() -> None:
    config, error = _call(tree_pct_str="60", water_pct_str="40")
    assert config is not None and error == ""


# ---------------------------------------------------------------------------
# Valeurs non numériques
# ---------------------------------------------------------------------------

def test_non_numeric_width_returns_error() -> None:
    config, error = _call(width_str="abc")
    assert config is None and error != ""


def test_non_numeric_height_returns_error() -> None:
    config, error = _call(height_str="")
    assert config is None and error != ""


def test_non_numeric_percentage_returns_error() -> None:
    config, error = _call(tree_pct_str="fifty")
    assert config is None and error != ""


def test_non_numeric_seed_returns_error() -> None:
    config, error = _call(seed_str="auto")
    assert config is None and error != ""


# ---------------------------------------------------------------------------
# Dimensions invalides
# ---------------------------------------------------------------------------

def test_zero_width_returns_error() -> None:
    config, error = _call(width_str="0")
    assert config is None and error != ""


def test_negative_height_returns_error() -> None:
    config, error = _call(height_str="-5")
    assert config is None and error != ""


# ---------------------------------------------------------------------------
# Pourcentages invalides
# ---------------------------------------------------------------------------

def test_tree_percentage_above_100_returns_error() -> None:
    config, error = _call(tree_pct_str="110")
    assert config is None and error != ""


def test_water_percentage_negative_returns_error() -> None:
    config, error = _call(water_pct_str="-1")
    assert config is None and error != ""


def test_percentage_sum_above_100_returns_error() -> None:
    config, error = _call(tree_pct_str="70", water_pct_str="40")
    assert config is None and error != ""
