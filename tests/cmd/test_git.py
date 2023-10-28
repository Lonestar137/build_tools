import os
from pathlib import Path
from build_tools.context.context_dir import Dir
from build_tools.cmd.git import GitRepo


tmp_dir = "@tmp"


def test_dir():
    with Dir(f"{tmp_dir}/directory"):
        with Dir("subdir"):
            assert Path(
                "../subdir").exists(), "Failed to create sub directory."

    assert Path(
        f"{tmp_dir}/directory").exists(), "Failed to create (multi)directory"


def test_clone():
    with Dir(f"{tmp_dir}"):
        req_repo = GitRepo("https://github.com/zpqrtbnk/test-repo.git")
        req_repo.clone()

        req_repo.clone("renamed-repo")

    assert Path(f"{tmp_dir}/test-repo").exists(), "Cloned repo does not exist."
    assert Path(
        f"{tmp_dir}/renamed-repo").exists(), "Cloned repo was not renamed."
    assert Path(
        f"{tmp_dir}/test-repo/.git").exists(), "Cloned repo was not a git repo."
    assert Path(
        f"{tmp_dir}/renamed-repo/.git").exists(), "Cloned repo  was not a git repo."


def test_cleanup():
    with Dir(f"{tmp_dir}", remove_after=True):
        pass

    assert not Path(tmp_dir).exists()
