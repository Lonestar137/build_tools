import os
import platform
import subprocess
import pytest
from pathlib import Path
from build_tools.context.venv import Venv
from build_tools.context.dir import Dir


test_venv = "test_venv"
test_dir = Path("@tmp") / test_venv


# with Dir(test_dir / "test_venv", remove_after=False):

def test_context():
    with Dir(test_dir, remove_after=False):
        with Venv(test_venv):
            if platform.os == "nt":
                assert Path(f"{test_venv}/Scripts").exists()
            else:
                assert Path(f"{test_venv}/bin").exists()


@pytest.mark.skip
def test_reuse_venv():
    with Dir(test_dir, remove_after=False):
        venv = Venv("venv")
        test_venv_path = Path(test_venv).absolute()

        def test_activate():
            venv.activate_venv()

            assert test_venv_path.__str__() == os.environ["VIRTUAL_ENV"]
            if platform.os == "nt":
                assert f"{test_venv_path}/Scripts" in os.environ["PATH"]
            else:
                assert f"{test_venv_path}/bin" in os.environ["PATH"]

        def test_deactivate():
            venv.deactivate_venv()
            try:
                os.environ["VIRTUAL_ENV"]
            except KeyError:
                assert True, "Env variable successfully deinitialized."
            except:
                assert False, "Got unexpected exception"

        test_activate()
        test_deactivate()


def test_install():
    requirements = ["qasync", "pytest"]
    with Dir(test_dir, remove_after=False):
        with Venv(test_venv, py_modules=requirements) as venv:
            extras = [
                "requests",
                "invoke"
            ]

            bin = None
            lib = f"{test_venv}/lib/"
            if platform.os == "nt":
                bin = Path(test_venv + "/Scripts/")
            else:
                bin = Path(test_venv + "/bin/")

            assert not Path(f"{bin}/invoke").exists()
            assert Path(f"{bin}/pytest").exists()
            # assert Path(f"venv/lib/").exists()

            venv.install(extras)
            assert Path(f"{bin}/invoke").exists()


def test_venv_install():

    pass


def test_cleanup():
    with Dir(test_dir, remove_after=True):
        pass
    assert not test_dir.exists()
