import pytest
from click.testing import CliRunner
from guix_env.cli import guix_env

# we reuse a bit of pytest's own testing machinery, this should eventually come
import subprocess


def test_cli():
    runner = CliRunner()
    result = runner.invoke(guix_env, ['create', 'test'])
    assert result.exit_code == 0
    result = runner.invoke(guix_env, ['info', 'test'])
    assert result.exit_code == 0

    result = runner.invoke(guix_env, ['list'])
    assert result.exit_code == 0
    result = runner.invoke(guix_env, ['run', 'test' , "ls"])
    assert result.exit_code == 0
    result = runner.invoke(guix_env, ['update'])
    assert result.exit_code == 0
    result = runner.invoke(guix_env, ['add-guix', 'rxvt-unicode'])
    assert result.exit_code == 0
    result = runner.invoke(guix_env, ['add-python', 'adastop'])
    assert result.exit_code == 0

    result = runner.invoke(guix_env, ['rm', 'test'])
    assert result.exit_code == 0
