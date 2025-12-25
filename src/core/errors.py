from __future__ import annotations


class AppError(Exception):
    """Базовая ошибка приложения."""


class ValidationError(AppError):
    """Ошибки валидации данных (ввод пользователя)."""


class DatabaseError(AppError):
    """Ошибки работы с БД (подключение/запросы)."""


