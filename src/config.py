from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import configparser


@dataclass(frozen=True, slots=True)
class MySqlConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


class ConfigError(RuntimeError):
    pass


def load_mysql_config(config_path: str | Path = "config.ini") -> MySqlConfig:
    path = Path(config_path)
    if not path.exists():
        raise ConfigError(
            f"Файл конфигурации не найден: {path}. Создайте его по образцу config.example.ini"
        )

    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")

    if "mysql" not in parser:
        raise ConfigError("В config.ini отсутствует секция [mysql].")

    sec = parser["mysql"]
    try:
        host = sec.get("host", "localhost")
        port = sec.getint("port", 3306)
        user = sec["user"]
        password = sec.get("password", "")
        database = sec["database"]
    except KeyError as e:
        raise ConfigError(f"В config.ini отсутствует обязательный ключ: {e}") from e

    return MySqlConfig(host=host, port=port, user=user, password=password, database=database)


