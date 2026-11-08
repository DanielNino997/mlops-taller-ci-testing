"""Funciones de preprocesamiento para el dataset Palmer Penguins."""

# Rangos aceptados (mínimo, máximo) para cada medida numérica
RANGES = {
    "bill_length_mm": (30.0, 60.0),
    "bill_depth_mm": (13.0, 22.0),
    "flipper_length_mm": (170.0, 235.0),
    "body_mass_g": (2500.0, 6500.0),
}

VALID_ISLANDS = ["biscoe", "dream", "torgersen"]
VALID_SEX = {"male": 1.0, "female": 0.0}

# Textos que en el dataset original significan "dato faltante"
MISSING_VALUES = {"", ".", "na", "nan", "none", "null"}

# Orden fijo de las columnas que recibe el modelo
FEATURE_NAMES = [
    "bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g",
    "island_biscoe", "island_dream", "island_torgersen",
    "sex_male", "bill_ratio",
]


def clean_text(value):
    """Función 1 - Limpieza de texto: '  Biscoe ' -> 'biscoe'."""
    if not isinstance(value, str):
        raise TypeError(f"se esperaba texto y llegó {type(value).__name__}")

    cleaned = " ".join(value.split()).lower()
    if cleaned in MISSING_VALUES:
        raise ValueError(f"valor faltante: {value!r}")
    return cleaned


def validate_range(name, value):
    """Función 2 - Validación de rangos: revisa que una medida tenga sentido."""
    if name not in RANGES:
        raise ValueError(f"columna desconocida: {name}")

    # bool es un tipo de int en Python (True == 1), por eso se excluye
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} debe ser numérico")

    low, high = RANGES[name]
    if not low <= value <= high:
        raise ValueError(f"{name}={value} fuera de rango [{low}, {high}]")
    return float(value)


def transform_features(record):
    """Función 3 - Transformación: convierte un registro en la lista que usa el modelo."""
    required = list(RANGES) + ["island", "sex"]
    missing = [col for col in required if col not in record]
    if missing:
        raise ValueError(f"faltan columnas: {missing}")

    # 4 medidas numéricas validadas
    numeric = [validate_range(col, record[col]) for col in RANGES]

    # isla -> 3 columnas 0/1 (one-hot)
    island = clean_text(record["island"])
    if island not in VALID_ISLANDS:
        raise ValueError(f"isla desconocida: {island}")
    island_one_hot = [1.0 if island == name else 0.0 for name in VALID_ISLANDS]

    # sexo -> 1 (male) o 0 (female)
    sex = clean_text(record["sex"])
    if sex not in VALID_SEX:
        raise ValueError(f"sexo desconocido: {sex}")

    # feature nueva: proporción largo/profundidad del pico
    bill_ratio = round(record["bill_length_mm"] / record["bill_depth_mm"], 4)

    return numeric + island_one_hot + [VALID_SEX[sex], bill_ratio]
