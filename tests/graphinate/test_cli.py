import sys

import pytest
from click.testing import CliRunner
from graphinate.cli import cli
from graphinate.tools.importer import ImportFromStringError


@pytest.fixture()
def runner():
    return CliRunner()


def test_save_model(octagonal_graph_model, runner):
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['save', '-m', octagonal_graph_model])
        assert result.exit_code == 0


def test_save_model_reference(runner):
    with runner.isolated_filesystem():
        sys.path.append('examples/math')
        result = runner.invoke(cli, ['save', '-m', "polygonal_graph:model"])
        assert result.exit_code == 0


def test_save_malformed_model_reference(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['save', '-m', "malformed_model_reference"])

    assert result.exit_code == 2
