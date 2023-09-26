import pytest
from click.testing import CliRunner

from graphinate.cli import cli


@pytest.fixture()
def runner():
    return CliRunner()


def test_save(octagonal_graph_model, runner):
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['save', '-m', octagonal_graph_model])
        assert result.exit_code == 0
