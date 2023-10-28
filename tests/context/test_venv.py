import os
import platform
from pathlib import Path
from build_tools.context.venv import Venv
from build_tools.context.context_dir import Dir


tmp_dir = Path("@tmp")


with Dir(tmp_dir / "test_venv", remove_after=False):
    def test_context():
        with Venv("venv"):
            if platform.os == "nt":
                assert Path("Scripts").exists()
            else:
                assert Path("bin").exists()

    def test_reuse_venv():
        venv = Venv("venv")

        def test_activate():
            venv.activate_venv()

        def test_deactivate():
            venv.deactivate_venv()

    def test_venv_install():
        pass
