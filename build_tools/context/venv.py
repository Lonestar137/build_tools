import os
import shutil
import subprocess
import platform
from pathlib import Path
from contextlib import AbstractContextManager


class Venv(AbstractContextManager):
    def __init__(self, path: str, mkdir=True, remove_after=False):
        self.start_dir = Path(os.getcwd()).absolute()
        self.venv_path = Path(path)
        self.mkdir = mkdir
        self.remove_after = remove_after
        self.venv_activated = False
        self.__error = None

    def __enter__(self):
        if self.mkdir:
            if self.__is_in_workspace():
                if not self.venv_path.is_dir():
                    print(f"Creating venv {self.venv_path}")
                    subprocess.run(["python", "-m", "venv", self.venv_path])

                self.activate_venv()
        return self

    def __exit__(self, x, y, z):
        if self.venv_activated:
            self.deactivate_venv()
        if self.remove_after and self.__is_in_workspace():
            print(f"Removing '{self.venv_path}' from '{self.start_dir}'")
            shutil.rmtree(self.venv_path)
        elif self.remove_after:
            print(f"Refusing to remove '{self.venv_path}'. {self.__error}")

    def activate_venv(self):
        if not self.venv_activated:
            if not self.venv_path.is_dir() or not self.__is_in_workspace():
                return

            activate_script = "activate"
            if os.name == "nt":
                activate_script = "Scripts/activate.bat"
            else:
                activate_script = "bin/activate"

            activate_script_path = self.venv_path / activate_script

            # Modify PATH directly to include the virtual environment's bin directory
            os.environ["PATH"] = f"{self.venv_path / 'bin'}:{os.environ['PATH']}"

            self.venv_activated = True

    def deactivate_venv(self):
        if self.venv_activated:
            # Restore the original PATH by removing the virtual environment's bin directory
            bin_path = self.venv_path / 'bin'
            os.environ["PATH"] = os.environ["PATH"].replace(f"{bin_path}:", "")
            self.venv_activated = False

    def __is_in_workspace(self):
        no_relative_path_char = ".." not in self.venv_path.__str__()
        is_sub_folder = self.venv_path.absolute().is_relative_to(self.start_dir)
        if not no_relative_path_char:
            self.__error = "Relative chars not allowed in path."
        if not is_sub_folder:
            self.__error = "Path must be a subfolder of the workspace."
        return is_sub_folder and no_relative_path_char
