from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, final

import nix_manipulator.parser
from nix_manipulator.expressions import AttributeSet, Binding, Primitive
from nix_manipulator.expressions.indented_string import IndentedString
from nix_manipulator.expressions.list import NixList

from util import strip_indented_string

PROJECTS = "projects"
ID = "id"
REQUIRES = "requires"
PORTS = "ports"
POST_INIT = "postInit"


@final
@dataclass(frozen=True)
class Project:
    id: str
    dependencies: list[str]
    port_names: list[str]
    post_init_script: str


@final
@dataclass(frozen=True)
class Config:
    projects: list[Project]

    def get_project(self, project_id: str) -> Project | None:
        for project in self.projects:
            if project.id == project_id:
                return project

        return None

    def walk_project_dependencies(
        self,
        project: Project,
        *,
        visited: set[str] | None = None,
    ) -> Generator[Project]:
        """Walk the dependency tree in order of declaration, skipping duplicates"""

        if visited is None:
            visited = set()

        visited.add(project.id)

        for dependency_id in project.dependencies:
            if dependency_id in visited:
                continue

            dep_project = self.get_project(dependency_id)
            if dep_project is None:
                raise ValueError(f"Dependency not found: {dependency_id!r}")

            yield dep_project
            yield from self.walk_project_dependencies(dep_project, visited=visited)


def parse_config(source_code: bytes | str | Path) -> Config:
    source = nix_manipulator.parser.parse(source_code)

    if len(source.value) != 1:
        raise ValueError("Expected exactly one top-level attribute set")

    toplevel: AttributeSet | Any = source.value.pop()
    if not isinstance(toplevel, AttributeSet):
        raise ValueError(f"Expected a top-level attribute set, got {type(toplevel)}")

    projects: list[Project] = []

    for val in toplevel.values:
        if not isinstance(val, Binding):
            raise ValueError(f"Expected a binding, got {type(val)}")

        # `projects` attrset with nested project definitions
        if val.name == PROJECTS:
            if not isinstance(val.value, AttributeSet):
                raise ValueError(
                    f"Expected an attribute set for projects, got {type(val.value)}"
                )

            for project_source in val.value.values:
                if not isinstance(project_source, Binding):
                    raise ValueError(f"Expected a binding, got {type(project_source)}")

                project = parse_project(project_source, project_source.name)
                projects.append(project)

        # Top-level `projects.<name>` definitions
        else:
            prefix, name = val.name.split(".", 1)
            if prefix != PROJECTS:
                continue

            project = parse_project(val, name)
            projects.append(project)

    return Config(projects=projects)


def parse_project(source: Binding, name: str) -> Project:
    if not isinstance(source.value, AttributeSet):
        raise ValueError(
            f"Expected an attribute set for project {name}, got {type(source.value)}"
        )

    parsed_id: str | None = None
    parsed_requires: list[str] = []
    parsed_ports: list[str] = []
    parsed_post_init: str | None = None

    for attribute in source.value.values:
        if not isinstance(attribute, Binding):
            raise ValueError(f"Expected a binding, got {type(attribute)}")

        if attribute.name == ID:
            parsed_id = parse_id(attribute)

        elif attribute.name == REQUIRES:
            parsed_requires = parse_requires(attribute)

        elif attribute.name == PORTS:
            parsed_ports = parse_port_names(attribute)

        elif attribute.name == POST_INIT:
            parsed_post_init = parse_post_init(attribute)

        else:
            raise ValueError(f"Unknown project attribute: {attribute.name!r}")

    if parsed_id is None:
        raise ValueError("Project attribute 'id' is required")

    if parsed_post_init is None:
        raise ValueError("Project attribute 'postInit' is required")

    return Project(
        id=parsed_id,
        dependencies=parsed_requires,
        port_names=parsed_ports,
        post_init_script=parsed_post_init,
    )


def parse_id(source: Binding) -> str:
    if not isinstance(source.value, Primitive):
        raise ValueError(f"Expected a primitive for id, got {type(source.value)}")
    return str(source.value.value)


def parse_requires(source: Binding) -> list[str]:
    if not isinstance(source.value, NixList):
        raise ValueError(f"Expected a list for requires, got {type(source.value)}")

    requires: list[str] = []
    for require in source.value.value:
        if not isinstance(require, Primitive):
            raise ValueError(f"Expected a primitive for require, got {type(require)}")
        requires.append(str(require.value))

    return requires


def parse_port_names(source: Binding) -> list[str]:
    if not isinstance(source.value, NixList):
        raise ValueError(f"Expected a list for ports, got {type(source.value)}")

    ports: list[str] = []
    for port in source.value.value:
        if not isinstance(port, Primitive):
            raise ValueError(f"Expected a primitive for port, got {type(port)}")
        ports.append(str(port.value))

    return ports


def parse_post_init(source: Binding) -> str:
    if not isinstance(source.value, IndentedString):
        raise ValueError(
            f"Expected an indented string for postInit, got {type(source.value)}"
        )

    return strip_indented_string(str(source.value.value)).strip()
