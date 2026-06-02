import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_core import from_json

type DbVersion = Literal[0]
type ConfigId = str
type ProjectId = str
type WorktreeName = str
type PortName = str


class Database(BaseModel):
    version: DbVersion
    configs: dict[ConfigId, Config]


class Config(BaseModel):
    path: Path
    projects: dict[ProjectId, Project]


class Project(BaseModel):
    worktrees: list[Worktree]

    def find_worktree(self, name: str) -> Worktree | None:
        for worktree in self.worktrees:
            if worktree.name == name:
                return worktree

        return None


class Worktree(BaseModel):
    name: WorktreeName
    path: Path
    ports: dict[PortName, int]
    # None -> No dependency provided, using custom ports
    dependencies: dict[ProjectId, WorktreeName | None]


def load_db(source: bytes | str | Path) -> Database:
    if isinstance(source, Path):
        with open(source, "r") as f:
            data = json.load(f)
    else:
        data = from_json(source)

    return Database(**data)


def write_db(db: Database, target: Path) -> None:
    serialized_db = db.model_dump(mode="json")

    with open(target, "w") as f:
        json.dump(serialized_db, f, indent=2)
