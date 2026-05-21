from dataclasses import dataclass
from pathlib import Path
from typing import Any, final

import nix_manipulator.parser
from nix_manipulator.expressions import AttributeSet, Binding

PROJECTS = "projects"


@final
@dataclass(frozen=True)
class Project:
    name: str
    dependencies: list[str]
    port_names: list[str]
    post_init_script: str


@final
@dataclass(frozen=True)
class Config:
    projects: list[Project]


def parse_config(path: Path) -> Config:
    source = nix_manipulator.parser.parse(path)

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
    print("parse project", name)

    return Project(
        name=name,
        dependencies=["TODO"],
        port_names=["TODO"],
        post_init_script="TODO",
    )
