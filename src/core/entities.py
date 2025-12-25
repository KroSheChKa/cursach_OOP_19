from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
import copy


@dataclass(slots=True)
class Client:
    id: Optional[int] = None
    name: str = ""
    phone: Optional[str] = None
    email: Optional[str] = None
    note: Optional[str] = None

    def clone(self) -> "Client":
        return copy.deepcopy(self)


@dataclass(slots=True)
class Employee:
    id: Optional[int] = None
    last_name: str = ""
    first_name: str = ""
    middle_name: Optional[str] = None
    position: str = ""
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True

    def full_name(self) -> str:
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(p for p in parts if p)

    def clone(self) -> "Employee":
        return copy.deepcopy(self)


@dataclass(slots=True)
class Project:
    id: Optional[int] = None
    client_id: int = 0
    name: str = ""
    description: Optional[str] = None
    start_date: date | None = None
    end_date: date | None = None
    status: str = "Active"

    def clone(self) -> "Project":
        return copy.deepcopy(self)


@dataclass(slots=True)
class Task:
    id: Optional[int] = None
    project_id: int = 0
    employee_id: Optional[int] = None
    title: str = ""
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    due_date: date | None = None
    completed_at: Optional[datetime] = None
    status: str = "New"

    def is_active(self) -> bool:
        return self.status in ("New", "InProgress")

    def clone(self) -> "Task":
        return copy.deepcopy(self)


@dataclass(slots=True)
class ProjectMember:
    project_id: int
    employee_id: int
    role: str = "Member"
    since_date: date | None = None


