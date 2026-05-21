import subprocess
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from config import parse_config
from env import get_base_env, get_port_env_var_name, get_random_port

app = App()


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
    env: dict[str, str] = {}

    if len(project.dependencies) > 0:
        for dependency in project.dependencies:
            dependency_project = config.get_project(dependency)
            if dependency_project is None:
                raise ValueError(f"Dependency not found: {dependency!r}")
            if len(dependency_project.dependencies) > 0:
                raise NotImplementedError(
                    "Nested dependency resolution is not yet implemented"
                )

            print(f"Dependency found: '{dependency_project.id}'")

            # TODO: Ask the user which worktree they want to use as the dependency
            # TODO: Get previously generated ports from some persistent config storage
            for port_name in dependency_project.port_names:
                port = input(f"Port number for '{port_name}': ")
                env_var_name = get_port_env_var_name(dependency_project.id, port_name)
                env[env_var_name] = port.strip()

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
        env=get_base_env() | env,
    )


if __name__ == "__main__":
    app()
