import inspect
import subprocess
from unittest.mock import ANY, MagicMock

import git as git_
import pytest
from git import exc as git_exceptions

from briefcase.config import AppConfig
from briefcase.console import Printer

from .utils import create_file


def pytest_sessionfinish(session, exitstatus):
    """When pytest is wrapping up, close the /dev/null file handle for the logfile Rich
    Console to avoid spurious ResourceWarning errors."""
    Printer.dev_null.close()


@pytest.fixture
def mock_git():
    git = MagicMock(spec_set=git_)
    git.exc = git_exceptions
    return git


# alias print() to allow non-briefcase code to use it
_print = print


def monkeypatched_print(*args, **kwargs):
    """Raise an error for calls to print() from briefcase."""
    frame = inspect.currentframe().f_back
    module = inspect.getmodule(frame.f_code)

    # Disallow any use of a bare print() in the briefcase codebase
    if module and module.__name__.startswith("briefcase."):
        pytest.fail(
            "print() should not be invoked directly. Use Log or Console for printing."
        )

    _print(*args, **kwargs)


@pytest.fixture(autouse=True)
def no_print(monkeypatch):
    """Replace builtin print function for ALL tests."""
    monkeypatch.setattr("builtins.print", monkeypatched_print)


@pytest.fixture
def sub_kw():
    """Default keyword arguments for all subprocess calls."""
    return dict(
        text=True,
        encoding=ANY,
        errors="backslashreplace",
    )


@pytest.fixture
def sub_check_output_kw(sub_kw):
    """Default keyword arguments for all subprocess.check_output calls."""
    return {
        **sub_kw,
        **dict(
            stderr=subprocess.STDOUT,
        ),
    }


@pytest.fixture
def sub_stream_kw(sub_kw):
    """Default keyword arguments for all output streaming subprocess calls."""
    return {
        **sub_kw,
        **dict(
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
        ),
    }


@pytest.fixture
def first_app_config():
    return AppConfig(
        app_name="first",
        bundle="com.example",
        version="0.0.1",
        description="The first simple app",
        sources=["src/first"],
    )


@pytest.fixture
def first_app_unbuilt(first_app_config, tmp_path):
    # The same fixture as first_app_config,
    # but ensures that the bundle for the app exists
    create_file(
        tmp_path
        / "base_path"
        / "build"
        / "first"
        / "tester"
        / "dummy"
        / "first.bundle",
        "first.bundle",
    )

    return first_app_config


@pytest.fixture
def first_app(first_app_unbuilt, tmp_path):
    # The same fixture as first_app_config,
    # but ensures that the binary for the app exists
    create_file(
        tmp_path / "base_path" / "build" / "first" / "tester" / "dummy" / "first.bin",
        "first.bin",
    )

    return first_app_unbuilt
