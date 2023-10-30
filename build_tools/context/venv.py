import os
import shlex
import shutil
import subprocess
import platform
from typing import List
from pathlib import Path
from contextlib import AbstractContextManager
from build.env import DefaultIsolatedEnv, _find_executable_and_scripts, _create_isolated_env_venv


class Venv(AbstractContextManager):
    def __init__(self, path: str, mkdir=True, remove_after=False, py_modules: List[str] = []):
        self.start_dir = Path(os.getcwd()).absolute()
        self.venv_path = Path(path).absolute()
        self.venv_python = None
        self.venv_bin = None
        self.vevn_lib = None
        self.mkdir = mkdir
        self.remove_after = remove_after
        self.venv_activated = False
        self.__error = None
        self.__pymodules = py_modules

    def __enter__(self):
        if self.mkdir:
            if self.__is_in_workspace():
                if not self.venv_path.is_dir():
                    print(f"Creating venv {self.venv_path}")
                    _create_isolated_env_venv(self.venv_path)
                try:
                    self.activate_venv()
                except Exception as e:
                    print(
                        f"There was a problem creating the Virtual environment {self.venv_path}")
                    print(e)
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

            self.venv_python, self.venv_bin, self.venv_lib = _find_executable_and_scripts(
                self.venv_path)

            # Modify PATH directly to include the virtual environment's bin directory
            self.__set_environ(using_venv=True)
            if self.__pymodules != []:
                self.install()

    def deactivate_venv(self):
        if self.venv_activated:
            # Restore the original PATH by removing the virtual environment's bin directory
            # bin_path = self.venv_path / 'bin'
            self.__set_environ(using_venv=False)

    def install(self, requirements: List[str] = None):
        if requirements:
            self.__pymodules.extend(requirements)
        for mod in self.__pymodules:
            cmd = [self.venv_python.__str__(), "-m", "pip",
                   "install"]
            cmd.extend(shlex.split(mod))
            subprocess.run(cmd)

    def __set_environ(self, using_venv=True):
        if using_venv:
            self.old_path = os.environ["PATH"]

            os.environ["PATH"] = f"{self.venv_bin}:{os.environ['PATH']}"
            os.environ["VIRTUAL_ENV"] = f"{self.venv_path.absolute()}"

            self.venv_activated = True
        else:
            if self.old_path:
                os.environ["PATH"] = self.old_path
            del os.environ["VIRTUAL_ENV"]
            self.venv_activated = False

    def __is_in_workspace(self):
        no_relative_path_char = ".." not in self.venv_path.__str__()
        is_sub_folder = self.venv_path.absolute().is_relative_to(self.start_dir)
        if not no_relative_path_char:
            self.__error = "Relative chars not allowed in path."
        if not is_sub_folder:
            self.__error = "Path must be a subfolder of the workspace."
        return is_sub_folder and no_relative_path_char
