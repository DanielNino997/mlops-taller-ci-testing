import pytest

from app.preprocessing import clean_text, transform_features, validate_range


# ---------- Función 1: clean_text ----------

def test_clean_text_quita_espacios_y_mayusculas():
    assert clean_text("  Biscoe  ") == "biscoe"


@pytest.mark.parametrize("value", ["", "   ", ".", "NA", "null"])
def test_clean_text_valor_faltante_lanza_error(value):
    with pytest.raises(ValueError, match="valor faltante"):
        clean_text(value)


def test_clean_text_no_texto_lanza_type_error():
    with pytest.raises(TypeError):
        clean_text(42)


# ---------- Función 2: validate_range ----------

def test_validate_range_valor_normal():
    assert validate_range("body_mass_g", 4000) == 4000.0


@pytest.mark.parametrize("value", [2500.0, 6500.0])
def test_validate_range_acepta_los_limites(value):
    assert validate_range("body_mass_g", value) == value


@pytest.mark.parametrize("value", [2499.9, 6500.1, -1])
def test_validate_range_fuera_de_rango_lanza_error(value):
    with pytest.raises(ValueError, match="fuera de rango"):
        validate_range("body_mass_g", value)


def test_validate_range_texto_lanza_type_error():
    with pytest.raises(TypeError):
        validate_range("body_mass_g", "4000")


def test_validate_range_columna_desconocida_lanza_error():
    with pytest.raises(ValueError, match="columna desconocida"):
        validate_range("peso_kg", 4)


# ---------- Función 3: transform_features ----------

def test_transform_features_registro_valido(valid_penguin):
    # Arrange: valid_penguin viene de la fixture en conftest.py
    # Act
    result = transform_features(valid_penguin)
    # Assert: 4 medidas + one-hot isla (Torgersen) + sexo male + bill_ratio
    assert result == [39.1, 18.7, 181.0, 3750.0, 0.0, 0.0, 1.0, 1.0, 2.0909]


def test_transform_features_limpia_texto_sucio(valid_penguin):
    valid_penguin["island"] = "  DREAM "
    valid_penguin["sex"] = "Female"
    result = transform_features(valid_penguin)
    assert result[4:8] == [0.0, 1.0, 0.0, 0.0]


def test_transform_features_falta_columna_lanza_error(valid_penguin):
    del valid_penguin["body_mass_g"]
    with pytest.raises(ValueError, match="faltan columnas"):
        transform_features(valid_penguin)


def test_transform_features_isla_desconocida_lanza_error(valid_penguin):
    valid_penguin["island"] = "Galapagos"
    with pytest.raises(ValueError, match="isla desconocida"):
        transform_features(valid_penguin)
