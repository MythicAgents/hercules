from CommandBase import *
from MythicFileRPC import *
import json


class ImportScriptArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "script": CommandParameter(
                name="script", type=ParameterType.File, description="script to import"
            )
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                raise ValueError("Missing JSON arguments")
        else:
            raise ValueError("Missing arguments")


class UploadCommand(CommandBase):
    cmd = "import_script"
    needs_admin = False
    help_cmd = "import_script"
    description = (
        "Import a third party PowerShell script into the agent's memory."
    )
    version = 1
    is_exit = False
    is_file_browse = False
    is_process_list = False
    is_download_file = False
    is_remove_file = False
    is_upload_file = False
    author = "@Airzero24"
    attackmapping = []
    argument_class = ImportScriptArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, response: AgentResponse):
        pass
