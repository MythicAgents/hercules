from CommandBase import *
import json
from MythicFileRPC import *


class LoadArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {}

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Need to specify commands to load")
        pass


class LoadCommand(CommandBase):
    cmd = "load_command"
    needs_admin = False
    help_cmd = "load cmd1 cmd2 cmd3..."
    description = "This loads new functions into memory via the C2 channel."
    version = 1
    is_exit = False
    is_file_browse = False
    is_process_list = False
    is_download_file = False
    is_remove_file = False
    is_upload_file = False
    author = "@its_a_feature_"
    parameters = []
    attackmapping = ["T1030", "T1129"]
    argument_class = LoadArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        total_code = ""
        for cmd in task.args.command_line.split(" "):
            cmd = cmd.strip()
            task.args.add_arg("cmd", cmd)
            try:
                code_path = self.agent_code_path / "{}.ps1".format(cmd)
                total_code += open(code_path, "r").read() + "\n"
            except Exception as e:
                raise Exception("Failed to find code for '{}'".format(cmd))
        task.args.add_arg("code", total_code)
        return task

    async def process_response(self, response: AgentResponse):
        pass
