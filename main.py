import subprocess
from pathlib import Path
from typing import Annotated, Literal

import inquirer
from cyclopts import App, Parameter

import db
from config import parse_config, validate_config
from db import load_db, write_db
from env import get_base_env, get_port_env_var_name, get_random_port

CUSTOM_WORKTREE = "__CUSTOM_WORKTREE__"
CustomWorktree = Literal["__CUSTOM_WORKTREE__"]


app = App()
app_config = App(name="config", help="Manage worktree configuration")
app.command(app_config)
app_db = App(name="db", help="Manage the worktree database")
app.command(app_db)


@app_config.command(name="show")
def config_show(
    *,
    config_path: Annotated[Path, Parameter("config", alias="-c")],
) -> int | None:
    """
    Parse and show the configuration file

    Parameters
    ----------
    config_path:
        Path to the worktree configuration file
    """

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config = parse_config(config_path)
    if diagnostics := validate_config(config):
        print("Configuration errors:")
        for diagnostic in diagnostics:
            print(f"  {diagnostic.project_id}: {diagnostic.message}")
        return 1

    print(f"Config '{config.id}'")
    if config.projects:
        for project in config.projects:
            print(f"  Project '{project.id}'")
            if project.dependencies:
                print(f"    Dependencies: {', '.join(project.dependencies)}")
            else:
                print("    Dependencies: <none>")
            if project.port_names:
                print(f"    Port names: {', '.join(project.port_names)}")
            else:
                print("    Port names: <none>")
    else:
        print("  No projects")


@app_db.command(name="show")
def db_show(
    *,
    # TODO)) Default to a common DB file location
    db_path: Annotated[Path, Parameter("db-path")],
    show_paths: Annotated[bool, Parameter("show-paths")] = False,
) -> int | None:
    """
    Show the contents of the database

    Parameters
    ----------
    db_path
        Path to the database file
    show_paths
        Show paths of configs and worktrees
    """

    db = load_db(db_path)

    print(f"Database file {db_path} (version {db.version}) is valid")
    print()

    if len(db.configs) == 0:
        print("No configs registered")

    for config_id, config in db.configs.items():
        print(f"Config '{config_id}'")
        if show_paths:
            print(f"  Path: {config.path}")

        if len(config.projects) == 0:
            print("  No projects registered")
            continue

        for project_id, project in config.projects.items():
            print(f"  Project '{project_id}'")
            if len(project.worktrees) == 0:
                print("    No worktrees registered")
                continue

            for worktree in project.worktrees:
                print(f"    Worktree '{worktree.name}'")
                if show_paths:
                    print(f"      Path: {worktree.path}")

                for port_name, port_number in worktree.ports.items():
                    env_var_name = get_port_env_var_name(project_id, port_name)
                    print(f"      Port '{port_name}': {port_number} ({env_var_name})")


@app.command
def register(
    *,
    # TODO)) Default to a common DB file location
    db_path: Annotated[Path, Parameter("db-path")],
    config_path: Annotated[Path, Parameter("config", alias="-c")],
    project_id: Annotated[str, Parameter("project", alias="-p")],
    worktree_path: Annotated[Path | None, Parameter("path", required=False)] = None,
    worktree_name: Annotated[str, Parameter("name", alias="-n")],
) -> int | None:
    """
    Register a worktree

    Parameters
    ----------
    db_path:
        Path to the database file
    config_path:
        Path to the worktree configuration file
    project_id:
        Project ID from the configuration file
    worktree_path:
        Path to the worktree (default: current directory)
    worktree_name:
        Name of the worktree
    """

    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    config_path = config_path.resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    if worktree_path is None:
        worktree_path = Path.cwd()
    worktree_path = worktree_path.resolve()
    if not worktree_path.exists():
        raise ValueError(f"Worktree path does not exist: '{worktree_path}'")

    database = load_db(db_path)

    config = parse_config(config_path)
    if diagnostics := validate_config(config):
        print("Configuration errors:")
        for diagnostic in diagnostics:
            print(f"  {diagnostic.project_id}: {diagnostic.message}")
        return 1

    project = config.get_project(project_id)
    if project is None:
        raise ValueError(f"Project not found: '{project_id}'")

    db_config = database.configs.get(config.id)
    if db_config is None:
        db_config = db.Config(path=config_path, projects={})
        database.configs[config.id] = db_config

    db_project = db_config.projects.get(project.id)
    if db_project is None:
        db_project = db.Project(worktrees=[])
        db_config.projects[project.id] = db_project

    # Make sure we don't register duplicate worktrees
    db_worktree = db_project.find_worktree(worktree_name)
    if db_worktree is not None:
        raise ValueError(f"Worktree already exists: '{worktree_name}'")

    selected_dependencies: dict[db.ProjectId, db.WorktreeName | None] = {}
    for dependency_id in project.dependencies:
        dependency = config.get_project(dependency_id)
        if dependency is None:
            raise ValueError(f"Dependency not found: '{dependency_id}'")

        choices: list[tuple[str, db.Worktree | str]] = []

        db_dependency = db_config.projects.get(dependency.id)
        if db_dependency:
            for worktree in db_dependency.worktrees:
                label = f"{worktree.name} ({worktree.path})"
                choices.append((label, worktree))

        choices.append(("Custom", CUSTOM_WORKTREE))
        selected_db_dependency: db.Worktree | CustomWorktree = inquirer.list_input(
            f"Which '{dependency.id}' worktree is a dependency?",
            choices=choices,
            carousel=True,
        )

        if selected_db_dependency == CUSTOM_WORKTREE:
            print(f"Using custom ports for '{dependency.id}'")
            selected_dependencies[dependency.id] = None
        else:
            print(f"Using '{dependency.id}' ports from '{selected_db_dependency.name}'")
            selected_dependencies[dependency.id] = selected_db_dependency.name

    # Manually input ports when registering an existing worktree
    ports: dict[db.PortName, int] = {}
    for port_name in project.port_names:
        port = input(f"Port number for {port_name}: ")
        ports[port_name] = int(port.strip())

    db_worktree = db.Worktree(
        name=worktree_name,
        path=worktree_path,
        ports=ports,
        dependencies=selected_dependencies,
    )
    db_project.worktrees.append(db_worktree)

    write_db(database, db_path)
    print(f"Saved updated db to {db_path}")


@app.command
def init(
    *,
    # TODO)) Default to a common DB file location
    db_path: Annotated[Path, Parameter("db-path")],
    config_path: Annotated[Path, Parameter("config", alias="-c")],
    project_id: Annotated[str, Parameter("project", alias="-p")],
    worktree_name: Annotated[str, Parameter("name", alias="-n")],
) -> int | None:
    """
    Initialize a worktree

    Parameters
    ----------
    db_path:
        Path to the database file
    config_path:
        Path to the worktree configuration file
    project_id:
        Project ID from the configuration file
    worktree_name:
        Name of the worktree
    """

    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    database = load_db(db_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config = parse_config(config_path)
    if diagnostics := validate_config(config):
        print("Configuration errors:")
        for diagnostic in diagnostics:
            print(f"  {diagnostic.project_id}: {diagnostic.message}")
        return 1

    project = config.get_project(project_id)
    if project is None:
        raise ValueError(f"Project not found: '{project_id}'")

    db_config = database.configs.get(config.id)
    if db_config is None:
        db_config = db.Config(path=config_path, projects={})
        database.configs[config.id] = db_config

    db_project = db_config.projects.get(project.id)
    if db_project is None:
        db_project = db.Project(worktrees=[])
        db_config.projects[project.id] = db_project

    # Make sure we don't register duplicate worktrees
    if db_project.find_worktree(worktree_name) is not None:
        raise ValueError(f"Worktree already exists: '{worktree_name}'")

    print(f"Initalizing worktree '{worktree_name}' for project '{project.id}'")
    env: dict[str, str] = {}
    selected_dependencies: dict[db.ProjectId, db.WorktreeName | None] = {}

    # TODO)) Only ask for direct dependencies
    for dependency in config.walk_project_dependencies(project):
        choices: list[tuple[str, db.Worktree | str]] = []

        db_dependency = db_config.projects.get(dependency.id)
        if db_dependency:
            for worktree in db_dependency.worktrees:
                label = f"{worktree.name} ({worktree.path})"
                choices.append((label, worktree))

        choices.append(("Provide ports manually", CUSTOM_WORKTREE))
        selected_db_dependency: db.Worktree | CustomWorktree = inquirer.list_input(
            f"Which '{dependency.id}' worktree should be used as a dependency?",
            choices=choices,
            carousel=True,
        )

        if selected_db_dependency == CUSTOM_WORKTREE:
            print(f"Using custom ports for '{dependency.id}'")
            selected_dependencies[dependency.id] = None
            for port_name in dependency.port_names:
                port = input(f"Port number for {dependency.id} -> {port_name}: ")
                env_var_name = get_port_env_var_name(dependency.id, port_name)
                env[env_var_name] = port.strip()
        else:
            print(f"Using '{dependency.id}' ports from '{selected_db_dependency.name}'")
            selected_dependencies[dependency.id] = selected_db_dependency.name
            for port_name, port_number in selected_db_dependency.ports.items():
                env_var_name = get_port_env_var_name(dependency.id, port_name)
                env[env_var_name] = str(port_number)

    print(f"Worktree name: {worktree_name}")
    env["WORKTREE_NAME"] = worktree_name

    generated_ports: dict[str, int] = {}
    if project.port_names:
        print(f"Ports: {', '.join(project.port_names)}")
        for port_name in project.port_names:
            port = get_random_port()
            generated_ports[port_name] = port
            env_var_name = get_port_env_var_name(project.id, port_name)
            env[env_var_name] = str(port)

    print(f"Env: {' '.join(f'{k}={v}' for k, v in env.items())}")

    print("Running post-init script...")
    post_init_result = subprocess.run(
        [
            "bash",
            "-euo",
            "pipefail",
            "-c",
            project.post_init_script,
        ],
        env=get_base_env() | env,
    )
    if post_init_result.returncode != 0:
        print(f"Post-init script failed with exit code {post_init_result.returncode}")
        exit(post_init_result.returncode)

    db_worktree = db.Worktree(
        name=worktree_name,
        path=Path.cwd().resolve(),
        ports=generated_ports,
        dependencies=selected_dependencies,
    )
    db_project.worktrees.append(db_worktree)

    write_db(database, db_path)
    print(f"Saved updated db to {db_path}")


if __name__ == "__main__":
    app()
