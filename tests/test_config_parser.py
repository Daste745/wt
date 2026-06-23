import pytest

from wt.config import parse_config


def test_blank_config() -> None:
    """Should raise a ValueError when parsing a blank config"""

    with pytest.raises(ValueError):
        parse_config("")


def test_empty_config_without_id() -> None:
    """Should raise a ValueError when parsing an empty config without an id"""

    with pytest.raises(ValueError):
        parse_config("{}")


def test_config_without_project() -> None:
    """Should return an empty Project when parsing a config with no project"""

    config = parse_config(r"""{ id = "test"; }""")
    assert len(config.projects) == 0


def test_toplevel_function() -> None:
    """Should raise a ValueError when parsing a top-level function"""

    with pytest.raises(ValueError):
        parse_config("{ ... }: {}")


@pytest.mark.parametrize(
    "source",
    [
        "{ projects.backend = {}; }",
        "{ projects = { backend = {}; }; }",
    ],
)
def test_parse_empty_project(source: str) -> None:
    """Should raise a ValueError when parsing an empty Project"""

    with pytest.raises(ValueError):
        parse_config(source)


def test_parse_other_toplevel_attrset() -> None:
    """Should ignore unknown top-level fields"""

    config = parse_config(r"""{ id = "test"; services.random = {}; projects = {}; }""")
    assert len(config.projects) == 0


def test_parse_project() -> None:
    """Should parse a project with all provided fields"""

    source = r"""
        {
            id = "test";
            projects.backend = {
                id = "backend";
                ports = [ "server" ];
                mainPort = "server";
                requires = [ "database" ];
                postInit = ''
                    sed -i "s/^PORT=.*\$/PORT=$BACKEND_SERVER_PORT/" .env
                '';
            };
        }
    """
    config = parse_config(source)
    assert len(config.projects) == 1
    assert config.projects[0].id == "backend"
    assert config.projects[0].port_names == ["server"]
    assert config.projects[0].main_port == "server"
    assert config.projects[0].dependencies == ["database"]
    assert config.projects[0].post_init_script.startswith("sed -i")


def test_parse_project_without_optional_fields() -> None:
    """Should parse a project, ignoring optional fields"""

    source = r"""
        {
            id = "test";
            projects.backend = {
                id = "backend";
                postInit = '''';
            };
        }
    """
    config = parse_config(source)
    assert len(config.projects) == 1
    assert config.projects[0].id == "backend"
    assert config.projects[0].port_names == []
    assert config.projects[0].main_port is None
    assert config.projects[0].dependencies == []
    assert config.projects[0].post_init_script == ""
