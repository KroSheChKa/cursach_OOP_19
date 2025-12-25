from __future__ import annotations

from datetime import datetime
import re

from src.core.errors import ValidationError


_CYR = "А-Яа-яЁё"
_ROMAN = "IV"
_ALLOWED_NAME_RE = re.compile(rf"^[{_CYR}{_ROMAN}\-\.,'’\(\) ]+$")
_HAS_CYR_RE = re.compile(rf"[{_CYR}]")
_LATIN_RE = re.compile(r"[A-Za-z]")

_SPECIAL_CHARS = set(" -.,'’()")


def require_non_empty(value: str, field_name: str) -> str:
    v = value.strip()
    if not v:
        raise ValidationError(f"Поле «{field_name}» обязательно для заполнения.")
    return v


def validate_email_optional(email: str | None) -> None:
    if email is None:
        return
    e = email.strip()
    if not e:
        return
    # Простая проверка, достаточная для курсовой
    if "@" not in e or "." not in e:
        raise ValidationError("Некорректный email.")


def validate_completed_at_not_future(completed_at: datetime | None) -> None:
    if completed_at is None:
        return
    now = datetime.now()
    if completed_at > now:
        raise ValidationError("Дата завершения не может быть больше текущей даты/времени.")


def validate_person_name_part(part: str, field_name: str) -> str:
    """
    Валидация части ФИО (Фамилия/Имя/Отчество) по ограниченному набору правил из методички.

    Допускаются: кириллица (вкл. Ё/ё), пробел, -, ., ' / ’, запятая, скобки (), I/V (прописные).
    """
    p = require_non_empty(part, field_name)

    if not _ALLOWED_NAME_RE.fullmatch(p):
        raise ValidationError(
            f"Поле «{field_name}» содержит недопустимые символы. Разрешены: кириллица, пробел, -, ., ', ’, , , (), I/V."
        )

    # Запрет любых латинских букв, кроме I и V (и только в верхнем регистре)
    for m in _LATIN_RE.finditer(p):
        ch = m.group(0)
        if ch not in ("I", "V"):
            raise ValidationError(f"Поле «{field_name}»: латинские буквы, кроме I/V, запрещены.")

    # Должна быть хотя бы одна кириллическая буква (чтобы не проходили строки вида "IV")
    if _HAS_CYR_RE.search(p) is None:
        raise ValidationError(f"Поле «{field_name}» должно содержать хотя бы одну кириллическую букву.")

    # I/V не могут быть первым символом
    if p[0] in ("I", "V"):
        raise ValidationError(f"Поле «{field_name}»: I/V не могут быть первым символом.")

    # Запрет "пунктуации" на краях
    forbidden_first = set("-.'’ ,") | {")", "("}
    forbidden_last = set("-.'’ ,") | {"("}
    if p[0] in forbidden_first:
        raise ValidationError(f"Поле «{field_name}» не может начинаться с символа «{p[0]}».")
    if p[-1] in forbidden_last:
        raise ValidationError(f"Поле «{field_name}» не может заканчиваться символом «{p[-1]}».")

    # Запрет подряд идущих спецсимволов (включая пробелы и скобки)
    for a, b in zip(p, p[1:]):
        if a in _SPECIAL_CHARS and b in _SPECIAL_CHARS:
            raise ValidationError(
                f"Поле «{field_name}»: запрещены подряд идущие спецсимволы (например, \"{a}{b}\")."
            )

    # Скобки должны быть парными и корректными
    depth = 0
    max_depth = 0
    prev = ""
    for ch in p:
        if ch == "(":
            if prev == "(":
                raise ValidationError(f"Поле «{field_name}»: запрещены подряд идущие символы \"((\".")
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == ")":
            depth -= 1
            if depth < 0:
                raise ValidationError(f"Поле «{field_name}»: неверная расстановка скобок.")
        prev = ch

    if depth != 0:
        raise ValidationError(f"Поле «{field_name}»: скобки должны быть парными.")
    if max_depth > 1:
        raise ValidationError(f"Поле «{field_name}»: вложенные скобки не допускаются.")
    if "()" in p:
        raise ValidationError(f"Поле «{field_name}»: пустые скобки () не допускаются.")

    return p


def validate_employee_fio(last_name: str, first_name: str, middle_name: str | None) -> tuple[str, str, str | None]:
    ln = validate_person_name_part(last_name, "Фамилия")
    fn = validate_person_name_part(first_name, "Имя")
    mn = None
    if middle_name is not None and middle_name.strip():
        mn = validate_person_name_part(middle_name, "Отчество")
    return ln, fn, mn


