from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import shlex

class ShellArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class ShellCommand(CommandBase):
    cmd = "shell"
    needs_admin = False
    help_cmd = "shell [command]"
    description = "Execute a shell command with 'bash -c' or 'cmd.exe /c'"
    version = 1
    author = "@xorrior"
    argument_class = ShellArguments
    attackmapping = ["T1059.004"]
    attributes = CommandAttributes(
        supported_os=[SupportedOS.MacOS, SupportedOS.Linux, SupportedOS.Windows],
        builtin=True,
        suggested_command=True,
    )

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        passed_args = shlex.split(taskData.args.command_line)
        if taskData.Payload.OS == "Windows":
            taskData.args.add_arg(
                "path", "C:\\Windows\\System32\WindowsPowerShell\\v1.0\\powershell.exe"
            )
            passed_args.insert(0, "/c")
        else:
            taskData.args.add_arg("path", "/bin/bash")
            passed_args.insert(0, "-c")
        taskData.args.add_arg("args", passed_args, type=ParameterType.Array)
        response.DisplayParams = taskData.args.get_arg("path") + " " + " ".join(passed_args)
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp