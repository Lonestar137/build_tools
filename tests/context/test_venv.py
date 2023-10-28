import os
import platform
import subprocess
from pathlib import Path
from build_tools.context.venv import Venv
from build_tools.context.context_dir import Dir


tmp_dir = Path("@tmp")
test_venv = "test_venv"


# with Dir(tmp_dir / "test_venv", remove_after=False):

def test_context():
    with Dir(tmp_dir / "test_venv", remove_after=False):
        with Venv(test_venv):
            if platform.os == "nt":
                assert Path(f"{test_venv}/Scripts").exists()
            else:
                assert Path(f"{test_venv}/bin").exists()


def test_reuse_venv():
    with Dir(tmp_dir / "test_venv", remove_after=False):
        venv = Venv("venv")
        test_venv_path = Path(test_venv).absolute()

        def test_activate():
            venv.activate_venv()
            breakpoint()

            assert test_venv_path.__str__() == os.environ["VIRTUAL_ENV"]
            if platform.os == "nt":
                assert f"{test_venv_path}/Scripts" in os.environ["PATH"]
            else:
                assert f"{test_venv_path}/bin" in os.environ["PATH"]

        # def test_deactivate():
        #     venv.deactivate_venv()
        #     try:
        #         os.environ["VIRTUAL_ENV"]
        #     except KeyError:
        #         assert True, "Env variable successfully deinitialized."
        #     except:
        #         assert False, "Got unexpected exception"

        test_activate()
        # test_deactivate()


def test_install():
    requirements = ["qasync", "pytest"]
    with Dir(tmp_dir / "test_venv", remove_after=False):
        with Venv("venv", py_modules=requirements) as venv:
            extras = [
                "requests",
                "invoke"
            ]

            bin = None
            if platform.os == "nt":
                bin = Path("venv/Scripts/")
            else:
                bin = Path("venv/bin/")

            assert not Path(f"{bin}/invoke").exists()
            assert Path(f"{bin}/pytest").exists()

            venv.install(extras)
            assert Path(f"{bin}/invoke").exists()

            # subprocess.run(["invoke", "--help"], stdout=subprocess.PIPE)
            subprocess.run(["invoke", "--help"])


def test_venv_install():

    pass
