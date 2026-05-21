import os
import random


def get_base_env() -> dict[str, str]:
    return {
        # TODO: Build a sandboxed environment with programs required to initialize a worktree,
        #       potentially allowing to specify extra programs in the config,
        #       similar to `runtimeInputs` in `pkgs.writeShellApplication`.
        "PATH": os.environ.get("PATH", ""),
    }


def get_random_port() -> int:
    return random.randint(1024, 65535)


def get_port_env_var_name(project_name: str, port_name: str) -> str:
    return f"{project_name.upper()}_{port_name.upper()}_PORT"
