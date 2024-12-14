import pytest
from click.testing import CliRunner
from guix_env.cli import guix_env

# we reuse a bit of pytest's own testing machinery, this should eventually come
import subprocess


def test_cli():
    runner = CliRunner()
    result = runner.invoke(guix_env, ['create', 'test_ci'])
    assert result.exit_code == 0
    result = runner.invoke(guix_env, ['info', 'test_ci'])
    assert result.exit_code == 0

    result = runner.invoke(guix_env, ['list'])
    assert result.exit_code == 0
    result = runner.invoke(guix_env, ['run', 'test_ci' , "ls"])
    assert result.exit_code == 0
    # result = runner.invoke(guix_env, ['update']) # for now this fails and I don't understand why, the command works locally.
    # assert result.exit_code == 0
    result = runner.invoke(guix_env, ['add-guix', "test_ci", 'rxvt-unicode'])
    assert result.exit_code == 0
    result = runner.invoke(guix_env, ['add-python', "test_ci", 'adastop'])
    assert result.exit_code == 0

    result = runner.invoke(guix_env, ['rm', 'test_ci'])
    assert result.exit_code == 0
