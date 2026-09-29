import os
import subprocess
import sys
from pathlib import Path

import pytest

import dotenv_fixed


@pytest.mark.parametrize(
    "call",
    [
        "load_dotenv(dotenv_fixed_path=Path('../.env'))\nprint(os.environ['a'])",
        "load_dotenv(dotenv_fixed_path='../.env')\nprint(os.environ['a'])",
        "print(dotenv_values(dotenv_fixed_path=Path('../.env'))['a'])",
    ],
)
def test_fixed_path_is_resolved_from_caller_file(tmp_path, call):
    (tmp_path / ".env").write_text("a=from_caller_parent")
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    code_path = src_dir / "code.py"
    code_path.write_text(
        "import os\nfrom pathlib import Path\n"
        "from dotenv_fixed import dotenv_values, load_dotenv\n" + call + "\n"
    )
    # Run from an unrelated directory that has its own ../.env to make sure
    # the current working directory is not used.
    cwd = tmp_path / "other" / "cwd"
    cwd.mkdir(parents=True)
    (tmp_path / "other" / ".env").write_text("a=from_cwd_parent")

    result = subprocess.run(
        [sys.executable, str(code_path)],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout == "from_caller_parent\n"


def test_resolve_fixed_path_uses_caller_directory():
    here = os.path.dirname(os.path.abspath(__file__))

    assert dotenv_fixed.resolve_fixed_path("x/.env") == os.path.join(here, "x/.env")


def test_resolve_fixed_path_keeps_absolute_path(tmp_path):
    path = str(tmp_path / ".env")

    assert dotenv_fixed.resolve_fixed_path(Path(path)) == path


def test_dotenv_path_still_works_like_upstream(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("a=b")
    monkeypatch.chdir(tmp_path)

    assert dotenv_fixed.dotenv_values(".env") == {"a": "b"}
    assert dotenv_fixed.dotenv_values(dotenv_path=".env") == {"a": "b"}


def test_other_arguments_are_passed_through(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("A_FIXED_TEST=new")
    monkeypatch.setenv("A_FIXED_TEST", "old")

    dotenv_fixed.load_dotenv(dotenv_fixed_path=tmp_path / ".env", override=True)

    assert os.environ["A_FIXED_TEST"] == "new"


@pytest.mark.parametrize(
    "args,kwargs", [(("a.env",), {}), ((), {"dotenv_path": "a.env"})]
)
def test_both_paths_raise(args, kwargs):
    with pytest.raises(TypeError):
        dotenv_fixed.load_dotenv(*args, dotenv_fixed_path="b.env", **kwargs)
