from config import Config, Project, validate_config


def test_validate_empty_config() -> None:
    """Shouldn't return any diagnostics for an empty config"""

    config = Config(projects=[])
    assert validate_config(config) == []


def test_validate_duplicate_project_id() -> None:
    """Should return a diagnostic for duplicate project IDs"""

    config = Config(
        projects=[
            Project(id="foo", dependencies=[], port_names=[], post_init_script=""),
            Project(id="bar", dependencies=["foo"], port_names=[], post_init_script=""),
            Project(id="foo", dependencies=[], port_names=[], post_init_script=""),
        ]
    )
    diagnostics = validate_config(config)
    assert len(diagnostics) == 1
    assert diagnostics[0].project_id == "foo"
    assert diagnostics[0].message.startswith("Duplicate project ID")


def test_validate_multiple_duplicate_project_ids() -> None:
    """Should return a diagnostic for all duplicate project IDs"""

    config = Config(
        projects=[
            Project(id="foo", dependencies=[], port_names=[], post_init_script=""),
            Project(id="baz", dependencies=["bar"], port_names=[], post_init_script=""),
            Project(id="bar", dependencies=["foo"], port_names=[], post_init_script=""),
            Project(id="foo", dependencies=[], port_names=[], post_init_script=""),
            Project(id="baz", dependencies=["bar"], port_names=[], post_init_script=""),
        ]
    )
    diagnostics = validate_config(config)
    assert len(diagnostics) == 2
    assert diagnostics[0].project_id == "foo"
    assert diagnostics[0].message.startswith("Duplicate project ID")
    assert diagnostics[1].project_id == "baz"
    assert diagnostics[1].message.startswith("Duplicate project ID")


def test_validate_unknown_dependency() -> None:
    """Should return a diagnostic for an unknown dependency ID"""

    config = Config(
        projects=[
            Project(id="foo", dependencies=["bar"], port_names=[], post_init_script=""),
        ]
    )
    diagnostics = validate_config(config)
    assert len(diagnostics) == 1
    assert diagnostics[0].project_id == "foo"
    assert diagnostics[0].message.startswith("Unknown dependency")


def test_validate_multiple_unknown_dependencies() -> None:
    """Should return a diagnostic for all unknown dependency IDs"""

    config = Config(
        projects=[
            Project(
                id="foo",
                dependencies=["bar", "baz"],
                port_names=[],
                post_init_script="",
            ),
        ]
    )
    diagnostics = validate_config(config)
    assert len(diagnostics) == 2
    assert diagnostics[0].project_id == "foo"
    assert diagnostics[0].message.startswith("Unknown dependency")
    assert diagnostics[1].project_id == "foo"
    assert diagnostics[1].message.startswith("Unknown dependency")
