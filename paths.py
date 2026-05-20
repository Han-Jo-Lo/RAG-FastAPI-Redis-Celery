from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent

VECTOR_DB_ROOT = BASE_DIR / "vector_dbs"


def _safe_db_slug(name: str) -> str:
    base = Path(name).name  
    if base in ("", ".", "..") or ".." in name:
        raise ValueError("nombre de base de datos inválido")

    if not re.fullmatch(r"[A-Za-z0-9._-]+", base):
        raise ValueError("nombre de base de datos contiene caracteres no permitidos")
    return base


def vector_db_path(name: str) -> Path:
    slug = _safe_db_slug(name)
    path = (VECTOR_DB_ROOT / slug).resolve()
    try:
        path.relative_to(VECTOR_DB_ROOT.resolve())
    except ValueError:
        raise ValueError("ruta fuera de vector_dbs") from None
    return path


