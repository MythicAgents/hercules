from CommandBase import *
import json


class JobKillArguments(TaskArguments):

    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {}

    async def parse_arguments(self):
        if len(self.command_line.strip()) == 0:
            raise Exception("A task_id is required to kill a job.")
        pass


class JobKillCommand(CommandBase):
    cmd = "job_kill"
    needs_admin = False
    help_cmd = "job_kill [task_id]"
    description = "Kill a long running job and return anyway output"
    version = 1
    is_exit = False
    is_file_browse = False
    is_process_list = False
    is_download_file = False
    is_remove_file = False
    is_upload_file = False
    author = "@Airzero24"
    argument_class = JobKillArguments
    attackmapping = []

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, response: AgentResponse):
        pass
