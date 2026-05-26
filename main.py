import subprocess
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from config import parse_config, validate_config
from env import get_base_env, get_port_env_var_name, get_random_port

app = App()


@app.command
def init(
    *,
    config_path: Annotated[Path, Parameter("config", alias="-c")],
    project_id: Annotated[str, Parameter("project", alias="-p")],
    worktree_name: Annotated[str, Parameter("name", alias="-n")],
) -> int | None:
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
    if diagnostics := validate_config(config):
        print("Configuration errors:")
        for diagnostic in diagnostics:
            print(f"  {diagnostic.project_id}: {diagnostic.message}")
        return 1

    project = config.get_project(project_id)
    if project is None:
        raise ValueError(f"Project not found: {project_id!r}")

    print(f"Initalizing project '{project.id}'")
    env: dict[str, str] = {}

    for dependency in config.walk_project_dependencies(project):
        # TODO: Ask the user which worktree they want to use as the dependency
        # TODO: Get previously generated ports from some persistent config storage
        for port_name in dependency.port_names:
            port = input(f"Port number for {dependency.id} -> {port_name}: ")
            env_var_name = get_port_env_var_name(dependency.id, port_name)
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
