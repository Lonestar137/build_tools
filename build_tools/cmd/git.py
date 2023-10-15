import shlex
import subprocess
import platform
from pathlib import Path


class GitRepo:
    def __init__(self, uri: str, submodules=False):
        self.submodules = submodules
        self.uri = uri
        self.git_cmd = "git"
        self.git_cmd_args = []
        self.cmds_to_run = []
        self.repo_name = uri.split('/')[-1][:-4]

    def clone(self, folder_name: str = None):
        cmd = None
        if folder_name:
            self.repo_name = folder_name
            cmd = [self.git_cmd, "clone", self.uri, folder_name]
        else:
            cmd = [self.git_cmd, "clone", self.uri]
        self.cmds_to_run.append(cmd)
        if self.submodules:
            sub_cmd = [self.git_cmd, "submodules",
                       "update", "--init", "--recursive"]
            self.cmds_to_run.append(sub_cmd)
        return self


class PythonGitRepo(GitRepo):
    def __init__(self, uri, submodules=False):
        super.__init__(self, uri, submodules)
        self.mode = "install"
        self.__venv = None

        self.python_cmd = None
        if platform.os == "nt":
            self.python_cmd = ["py", "-3"]
        else:
            self.python_cmd = ["/usr/bin/env", "python"]

        self.python_cmd_args = []

    def set_requirements_file(self, file_path: str = "requirements.txt"):
        self.python_cmd_args.extend(["--requirement", file_path])
        return self

    def set_editable(self):
        self.python_cmd_args.append("-e")
        return self

    def set_find_links(self, dest):
        self.python_cmd_args.extend(["--find-links", dest])
        return self

    def use_venv(self, path: str):
        self.__venv = path
        if platform.os == "nt":
            # TODO: detect if cmd prompt or powershell.
            self.cmds_to_run.append(
                Path(f"{path}/Scripts/Activate.ps").__str__())
        else:
            self.cmds_to_run.append(
                Path(f"source {path}/bin/activate").__str__())

        cmd = self.python_cmd.copy()
        cmd.extend(["-m", "venv", path])
        self.cmds_to_run.append(cmd)

    def wheels(self, dest: str):
        cmd = self.python_cmd.copy()
        if "--requirement" in self.python_cmd_args:
            cmd.extend(["wheel"])
        else:
            cmd.extend(["wheel", "."])
        self.cmds_to_run.append(cmd + self.python_cmd_args)
        return self

    def install(self):
        return self

    def build(self):
        print("build . . .")
        print(self.cmds_to_run)
        # for cmd in self.cmds_to_run:
        #     subprocess.run(cmd)


if __name__ == "__main__":
    m3 = GitRepo("git@", submodules=True)
    m3.clone()

    py3 = PythonGitRepo("github.com....", submodules=True)
    py3.set_editable().set_requirements_file()
    py3.clone()
