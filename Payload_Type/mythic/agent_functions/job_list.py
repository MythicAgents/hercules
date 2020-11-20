from CommandBase import *
import json


class JobListArguments(TaskArguments):

    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {}

    async def parse_arguments(self):
        pass


class JobListCommand(CommandBase):
    cmd = "job_list"
    needs_admin = False
    help_cmd = "job_list"
    description = "List current long running jobs."
    version = 1
    is_exit = False
    is_file_browse = False
    is_process_list = False
    is_download_file = False
    is_remove_file = False
    is_upload_file = False
    author = "@Airzero24"
    argument_class = JobListArguments
    attackmapping = []

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, response: AgentResponse):
        pass
