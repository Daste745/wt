import random
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from config import parse_config

app = App()


def get_random_port() -> int:
    return random.randint(1024, 65535)


def get_port_env_var_name(project_name: str, port_name: str) -> str:
    return f"{project_name.upper()}_{port_name.upper()}_PORT"


@app.command
def init(
    *,
    config_path: Annotated[Path, Parameter("config", alias="-c")],
    project_name: Annotated[str, Parameter("project", alias="-p")],
) -> None:
    """
    Initialize the worktree

    Parameters
    ----------
    config_path:
        Path to the worktree configuration file
    project_name:
        Project ID from the configuration file
    """

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    print(f"Init {project_name} from {config_path}")

    config = parse_config(config_path)
    print(config)


if __name__ == "__main__":
    app()
