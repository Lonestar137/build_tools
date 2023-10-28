import os
from pathlib import Path
from build_tools.context.context_dir import Dir
from build_tools.cmd.git import GitRepo, PythonGitRepo


tmp_dir = Path("@tmp/test_git")


with Dir(tmp_dir, remove_after=True):
    test_dir = f"{tmp_dir}"

    def test_create_dir():
        with Dir(f"{test_dir}/directory"):
            with Dir("subdir"):
                assert Path(
                    "../subdir").exists(), "Failed to create sub directory."

        assert Path(
            f"{test_dir}/directory").exists(), "Failed to create (multi)directory"

    def test_git_repo():
        with Dir(f"{test_dir}"):
            req_repo = GitRepo("https://github.com/zpqrtbnk/test-repo.git")
            req_repo.clone()

            req_repo.clone("renamed-repo")

        assert Path(
            f"{test_dir}/test-repo").exists(), "Cloned repo folder does not exist."
        assert Path(
            f"{test_dir}/renamed-repo").exists(), "Cloned repo was not renamed."
        assert Path(
            f"{test_dir}/test-repo/.git").exists(), "Cloned repo was not a git repo."
        assert Path(
            f"{test_dir}/renamed-repo/.git").exists(), "Cloned repo  was not a git repo."

    def test_python_repo():
        with Dir(Path(test_dir) / "python_test"):
            expected_wheels = ["peppercorn-",
                               "sampleproject-]"]
            sample = PythonGitRepo("https://github.com/pypa/sampleproject.git")
            sample.clone("sample")
            sample.wheels("wheelhouse")
            sample.build()

            assert Path(f"wheelhouse").exists()
            assert Path(f"sample/.git").exists()
            whls = Path(f"wheelhouse").glob("*.whl")
            i = 0
            # for w in whls:
            #     assert expected_wheels[i] in w, "Incorrect or missing wheels."
            #     i += 1

        assert Path(f"{test_dir}/python_test").exists()

    # TODO: Prevent making bad directory names.  I.e. if you pass a function to WithDir
    # TODO: Test that Path and str are treated the same/correctly.

    def test_cleanup():
        with Dir(f"test", remove_after=True):
            pass

        assert not Path("test").exists()
