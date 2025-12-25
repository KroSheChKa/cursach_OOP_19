from __future__ import annotations

from src.core.entities import Client
from src.core.validation import require_non_empty, validate_email_optional
from src.db.repositories.mysql.client_repo import ClientRepositoryMySql


class ClientService:
    def __init__(self, repo: ClientRepositoryMySql):
        self._repo = repo

    def list_clients(self) -> list[Client]:
        return self._repo.list_all()

    def create_client(self, c: Client) -> int:
        c.name = require_non_empty(c.name, "Название клиента")
        validate_email_optional(c.email)
        return self._repo.create(c)

    def update_client(self, c: Client) -> None:
        c.name = require_non_empty(c.name, "Название клиента")
        validate_email_optional(c.email)
        self._repo.update(c)

    def delete_client(self, client_id: int) -> None:
        self._repo.delete(client_id)


