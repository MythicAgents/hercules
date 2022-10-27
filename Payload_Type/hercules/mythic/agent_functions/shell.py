from mythic_payloadtype_container.MythicCommandBase import *
import shlex
from mythic_payloadtype_container.MythicRPC import *


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
    script_only = True
    supported_ui_features = ["callback_table:shell"]
    attributes = CommandAttributes(
        supported_os=[SupportedOS.MacOS, SupportedOS.Linux, SupportedOS.Windows],
        builtin=True,
        suggested_command=True,
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        passed_args = shlex.split(task.args.command_line)
        if task.callback.payload["os"] == "Windows":
            task.args.add_arg(
                "path", "C:\\Windows\\System32\WindowsPowerShell\\v1. 0\\powershell.exe"
            )
            passed_args.insert(0, "/c")
        else:
            task.args.add_arg("path", "/bin/bash")
            passed_args.insert(0, "-c")
        task.args.add_arg("args", passed_args, type=ParameterType.Array)
        task.display_params = task.args.get_arg("path") + " " + " ".join(passed_args)
        task.command_name = "run"
        return task

    async def process_response(self, response: AgentResponse):
        pass
