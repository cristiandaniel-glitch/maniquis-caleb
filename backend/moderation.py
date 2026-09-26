"""
Filtro de lenguaje ofensivo para textos públicos (reseñas).

Normaliza el texto (minúsculas, sin tildes, sustituciones tipo "p0t4",
letras repetidas y separadores entre letras) y busca palabras vulgares o
insultos comunes en el español del Perú. Se usa en el servidor para que
nadie pueda saltárselo desde el navegador.
"""

import re
import unicodedata

# Raíces: se detectan como palabra completa o como inicio de palabra
# ("cojud" cubre cojudo, cojuda, cojudez...).
_ROOTS = [
    "mierd", "carajo", "cojud", "huevon", "webon", "wevon", "cabron", "pendej",
    "conchatumadre", "conchasumadre", "concha de tu madre", "conchesumare",
    "chucha", "verga", "pinga", "put", "maricon", "marica", "imbecil", "idiot",
    "estupid", "culer", "cula", "joder", "jodid", "tarad",
    "pajer", "zorra", "perra", "malparid", "hijo de puta", "hdp", "ctm", "csm",
    "mrd", "ptm", "chupala", "chupame", "lameculo", "retrasad", "mongol", "cagad",
    "caca", "follar", "cachar", "cachero", "cabro", "rosquete",
]
# Palabras cortas que solo cuentan como palabra exacta (evitar falsos positivos
# como "computadora", "reputación", "disputa")
_EXACT = {"cula", "caca", "cabro"}

_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s", "!": "i"})


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn" or c == "̃")
    text = unicodedata.normalize("NFC", text).replace("ñ", "n")
    text = text.translate(_LEET)
    text = re.sub(r"(.)\1{2,}", r"\1", text)                 # "mieeeerda" -> "mierda"
    text = re.sub(r"(?<=\b\w)[\.\-_\*](?=\w\b)", "", text)   # "c.t.m" -> "ctm"
    return text


def _pattern(root: str) -> str:
    root = root.replace("ñ", "n")
    body = r"\s+".join(re.escape(part) for part in root.split())
    return rf"\b{body}\b" if root in _EXACT else rf"\b{body}"


_REGEX = re.compile("|".join(_pattern(r) for r in _ROOTS))
# Excepciones legítimas que empiezan igual que una raíz
_SAFE = re.compile(r"\b(putativ|putrefac|putrid|cabrona?l|marical|culata|culantro|cular)\w*")


def contains_profanity(text: str) -> bool:
    """True si el texto contiene lenguaje vulgar u ofensivo."""
    if not text:
        return False
    norm = _normalize(text)
    norm = _SAFE.sub(" ", norm)
    compact = re.sub(r"[^a-z\s]", "", norm)
    return bool(_REGEX.search(norm) or _REGEX.search(compact))
