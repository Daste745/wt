import os
import random
import subprocess
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from config import parse_config

app = App()


def get_random_port() -> int:
    return random.randint(1024, 65535)


def get_port_env_var_name(project_name: str, port_name: str) -> str:
    return f"{project_name.upper()}_{port_name.upper()}_PORT"


def get_env() -> dict[str, str]:
    return {
        # TODO: Build a sandboxed environment with programs required to initialize a worktree,
        #       potentially allowing to specify extra programs in the config,
        #       similar to `runtimeInputs` in `pkgs.writeShellApplication`.
        "PATH": os.environ.get("PATH", ""),
    }


@app.command
def init(
    *,
    config_path: Annotated[Path, Parameter("config", alias="-c")],
    project_id: Annotated[str, Parameter("project", alias="-p")],
    worktree_name: Annotated[str, Parameter("name", alias="-n")],
) -> None:
    """
    Initialize a worktree

    Parameters
    ----------
    config_path:
        Path to the worktree configuration file
    project_id:
        Project ID from the configuration file
    worktree_name:
        Name of the worktree
    """

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config = parse_config(config_path)

    project = config.get_project(project_id)
    if project is None:
        raise ValueError(f"Project not found: {project_id!r}")

    print(f"Initalizing project '{project.id}'")

    if len(project.dependencies) > 0:
        print(f"Dependencies: {', '.join(project.dependencies)}")
        # TODO: Resolve dependencies and their ports
        # TODO: Make sure all dependencies have been initialized
        # TODO: Load generated ports from dependencies
        # TODO: Ask the user which worktree they want to use as the dependency
        raise NotImplementedError("Dependency resolution is not yet implemented")

    env: dict[str, str] = {}
    print(f"Worktree name: {worktree_name}")
    env["WORKTREE_NAME"] = worktree_name

    print(f"Ports: {', '.join(project.port_names)}")
    # TODO: Write generated ports into some persistent config,
    #       so they can be reused by dependent projects
    for port_name in project.port_names:
        port = get_random_port()
        env_var_name = get_port_env_var_name(project.id, port_name)
        env[env_var_name] = str(port)

    print(f"Env: {' '.join(f'{k}={v}' for k, v in env.items())}")

    print("Running post-init script...")
    subprocess.run(
        [
            "bash",
            "-euo",
            "pipefail",
            "-c",
            project.post_init_script,
        ],
        env=get_env() | env,
    )


if __name__ == "__main__":
    app()
