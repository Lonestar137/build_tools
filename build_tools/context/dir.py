import os
import shutil
from pathlib import Path
from contextlib import AbstractContextManager


class Dir(AbstractContextManager):
    def __init__(self, path, mkdir=True, remove_after=False):
        self.start_dir = Path(os.getcwd()).absolute()

        self.path = path if type(path) == Path else Path(path)

        self.mkdir = mkdir
        self.remove_after = remove_after

        self.__error = None
        self.__is_in_workspace = self.__in_workspace()

    def __enter__(self):
        if self.mkdir and self.__is_in_workspace:
            if not self.path.is_dir():
                print(f"Creating {self.path}")
                self.path.mkdir(parents=True, exist_ok=True)
            else:
                print(f"Using existing directory: {self.path}")

        if self.__is_in_workspace:
            os.chdir(self.path)

        return self

    def __exit__(self, x, y, z):
        os.chdir(self.start_dir)
        if self.remove_after:
            if self.__is_in_workspace:
                print(f"Removing '{self.path}' from '{self.start_dir}'")
                shutil.rmtree(self.path)
            else:
                print(f"Refusing to remove '{self.path}'. {self.__error}")

    def __in_workspace(self):
        no_relative_path_char = ".." not in self.path.__str__()
        is_sub_folder = self.path.absolute().is_relative_to(self.start_dir)
        if not no_relative_path_char:
            self.__error = "Relative chars not allowed in path."

        if not is_sub_folder:
            self.__error = "Path must be a sub folder of the workspace."

        return is_sub_folder and no_relative_path_char


if __name__ == "__main__":
    mkdirs = True
    with Dir("build_tools/test", mkdirs):
        print(f"Inside {os.getcwd()}")
        with Dir("test2/", mkdirs):
            print(f"Inside2 {os.getcwd()}")
        with Dir("hello/", mkdirs):
            print(f"Inside hello {os.getcwd()}")
        with Dir("hello2/", mkdirs):
            print(f"Inside hello {os.getcwd()}")
