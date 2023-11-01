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
        self.repo_name = uri.split('/')[-1][:-4]
        self.cloned_state = False

    def clone(self, folder_name: str = None):
        cmd = None
        if folder_name:
            self.repo_name = folder_name
            cmd = [self.git_cmd, "clone", self.uri, folder_name]
        else:
            cmd = [self.git_cmd, "clone", self.uri]
        subprocess.run(cmd)
        if self.submodules:
            sub_cmd = [self.git_cmd, "submodules",
                       "update", "--init", "--recursive"]
            subprocess.run(sub_cmd)
        self.cloned_state = True
        return self


class PythonGitRepo(GitRepo):
    def __init__(self, uri, submodules=False):
        super().__init__(uri, submodules)
        self.__venv = None
        self.cmds_to_run = []

        self.python_cmd = ["python", "-m"]
        # if platform.os == "nt":
        #     self.python_cmd = ["py", "-3"]
        # else:
        #     self.python_cmd = ["/usr/bin/env", "python"]

        self.python_cmd_args = []
        self.modes = ["install", "wheel"]

    def set_requirements_file(self, file_path: str = "requirements.txt"):
        self.python_cmd_args.extend(["--requirement", file_path])
        return self

    def set_editable(self):
        self.python_cmd_args.append("--editable")
        return self

    def set_find_links(self, dest):
        self.python_cmd_args.extend(["--find-links", dest])
        return self

    def wheels(self, dest: str):
        cmd = self.python_cmd.copy()
        if "--requirement" in self.python_cmd_args:
            cmd.extend(["pip", "wheel", "-w", dest])
        else:
            cmd.extend(["pip", "wheel", "-w", dest, f"./{self.repo_name}"])
        self.cmds_to_run.append(cmd + self.python_cmd_args)
        return self

    def install(self):
        cmd = self.python_cmd.copy()
        if "--requirement" in self.python_cmd_args:
            cmd.extend(["pip", "install"])
        else:
            cmd.extend(["pip", "install", f"./{self.repo_name}"])
        self.cmds_to_run.append(cmd + self.python_cmd_args)
        return self

    def build(self):
        if not self.cloned_state:
            self.clone()
        print("Building with provided commands. . .")
        ran = False
        for cmd in self.cmds_to_run:
            print(cmd)
            for mode in self.modes:
                if mode in cmd:
                    subprocess.run(cmd)
                    ran = True
        if not ran:
            print(f"No valid command was provided: {self.cmds_to_run}")
