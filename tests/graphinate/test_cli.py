import sys

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
        result = runner.invoke(cli, ['save', '-m', octagonal_graph_model])
        assert result.exit_code == 0


def test_save_model_reference(runner):
    sys.path.append('examples/math')
    result = runner.invoke(cli, ['save', '-m', "polygonal_graph:model"])
    assert result.exit_code == 0


def test_save_malformed_model_reference(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['save', '-m', "malformed_model_reference"])

    assert result.exit_code == 2


def test_import_from_string():
    sys.path.append(EXAMPLES_MATH)
    actual = import_from_string("polygonal_graph:model")
    assert isinstance(actual, graphinate.GraphModel)
    assert actual.name == "Octagonal Graph"


import_from_string_error_cases = [
    ("does_not_exist:model", "Could not import module 'does_not_exist'."),
    ("polygonal_graph:does_not_exist", "Attribute 'does_not_exist' not found in module 'polygonal_graph'."),
    ("wrong_format", "Import string 'wrong_format' must be in format '<module>:<attribute>'.")
]


@pytest.mark.parametrize(('case', 'message'), import_from_string_error_cases)
def test_import_from_string__error(case, message):
    sys.path.append(EXAMPLES_MATH)
    with pytest.raises(ImportFromStringError, match=message):
        _ = import_from_string(case)


import_from_string_not_str_cases = [
    0,
    None
]


@pytest.mark.parametrize('case', import_from_string_not_str_cases)
def test_import_from_string__not_str(case):
    actual = import_from_string(case)
    assert actual == case
