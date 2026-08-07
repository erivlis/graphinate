import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

import graphinate
from graphinate.cli import ImportFromStringError, cli, import_from_string

EXAMPLES_MATH = 'examples/math'


@pytest.fixture
def runner():
    return CliRunner()


def test_save_model(octagonal_graph_model, runner):
    with runner.isolated_filesystem():
        # Act
        result = runner.invoke(cli, ['save', '-m', octagonal_graph_model])

        # Assert
        assert result.exit_code == 0


def test_save_model_reference(runner):
    # Arrange
    sys.path.append(str(Path(EXAMPLES_MATH).resolve()))

    with runner.isolated_filesystem():
        # Act
        result = runner.invoke(cli, ['save', '-m', "polygonal_graph:model"])

        # Assert
        assert result.exit_code == 0


def test_save_malformed_model_reference(runner):
    with runner.isolated_filesystem():
        # Act
        result = runner.invoke(cli, ['save', '-m', "malformed_model_reference"])

    # Assert
    assert result.exit_code == 2


def test_import_from_string():
    # Arrange
    sys.path.append(EXAMPLES_MATH)

    # Act
    actual = import_from_string("polygonal_graph:model")

    # Assert
    assert isinstance(actual, graphinate.GraphModel)
    assert actual.name == "Octagonal Graph"


import_from_string_error_cases = [
    ("does_not_exist:model", "Could not import module 'does_not_exist'."),
    ("polygonal_graph:does_not_exist",
     "Attribute 'does_not_exist' not found in import string reference 'polygonal_graph:does_not_exist'."),
    ("wrong_format", "Import string 'wrong_format' must be in format '<module>:<attribute>'.")
]


@pytest.mark.parametrize(('case', 'message'), import_from_string_error_cases)
def test_import_from_string__error(case, message):
    # Arrange
    sys.path.append(EXAMPLES_MATH)

    # Act & Assert
    with pytest.raises(ImportFromStringError, match=message):
        _ = import_from_string(case)


import_from_string_not_str_cases = [
    0,
    None
]


@pytest.mark.parametrize('case', import_from_string_not_str_cases)
def test_import_from_string__not_str(case):
    # Act & Assert
    with pytest.raises(ImportFromStringError, match=f"{case} is not a string"):
        _actual = import_from_string(case)


def test_import_from_string_not_a_graph_model():
    with pytest.raises(ImportFromStringError, match="GraphModel instance cannot be determined"):
        import_from_string("sys:path")


def test_import_from_string_nested_module_not_found(monkeypatch):
    import importlib
    def mock_import(name):
        raise ModuleNotFoundError("No module named 'other_pkg'", name="other_pkg")
    monkeypatch.setattr(importlib, 'import_module', mock_import)

    with pytest.raises(ModuleNotFoundError):
        import_from_string("some_module:model")


def test_save_model_file_exists_confirm(octagonal_graph_model, runner):
    with runner.isolated_filesystem():
        file_name = f"{octagonal_graph_model.name}.d3_graph.json"
        Path(file_name).write_text("{}")

        result = runner.invoke(cli, ['save', '-m', octagonal_graph_model], input='y\n')
        assert result.exit_code == 0


def test_server_command(octagonal_graph_model, runner, monkeypatch):
    import graphinate.renderers.graphql as graphql_renderer
    called = []
    def mock_server(schema, port, browse, **kwargs):
        called.append((port, browse))

    monkeypatch.setattr(graphql_renderer, 'server', mock_server)
    result = runner.invoke(cli, ['server', '-m', octagonal_graph_model, '-p', '8080'])
    assert result.exit_code == 0
    assert len(called) == 1
    assert called[0] == (8080, False)


def test_save_model_absolute_or_subdirectory_path(runner):
    import os
    m_subdir = graphinate.GraphModel('sub/dir_model')
    res_subdir = runner.invoke(cli, ['save', '-m', m_subdir])
    assert res_subdir.exit_code != 0
    assert "Saving to subdirectories is not supported" in res_subdir.output

    abs_name = os.path.abspath(os.sep + 'abs_model')
    m_abs = graphinate.GraphModel(abs_name)
    res_abs = runner.invoke(cli, ['save', '-m', m_abs])
    assert res_abs.exit_code != 0
    assert "Please provide a relative file path" in res_abs.output







