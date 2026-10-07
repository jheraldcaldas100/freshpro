import unicodedata


def normalizar(texto: str) -> str:
    """Clave de comparación: sin tildes, en minúsculas y con espacios simples."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return " ".join(sin_tildes.casefold().split())
