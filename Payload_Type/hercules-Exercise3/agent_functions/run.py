from mythic_container.MythicCommandBase import *
import shlex
from mythic_container.MythicRPC import *


class RunArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="path",
                cli_name="path",
                display_name="BinaryPath",
                type=ParameterType.String,
                description="Absolute path to the program to run",
                parameter_group_info=[ParameterGroupInfo(ui_position=1)],
            ),
            CommandParameter(
                name="args",
                cli_name="args",
                display_name="Arguments",
                type=ParameterType.Array,
                description="Array of arguments to pass to the program",
                parameter_group_info=[
                    ParameterGroupInfo(ui_position=2, required=False)
                ],
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)
        if self.get_arg("args") is None:
            self.add_arg("args", [])

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)
        if self.get_arg("args") is None:
            self.add_arg("args", [])


class RunCommand(CommandBase):
    cmd = "run"
    needs_admin = False
    help_cmd = "run -path /path/to/binary -args arg1 -args arg2 -args arg3"
    description = "Execute a command from disk with arguments"
    version = 1
    author = "@its_a_feature_"
    argument_class = RunArguments
    attackmapping = ["T1059.004"]
    attributes = CommandAttributes(
        supported_os=[SupportedOS.MacOS, SupportedOS.Linux, SupportedOS.Windows],
        builtin=True,
        suggested_command=True,
    )

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"{taskData.args.get_arg('path')} {taskData.args.get_arg('args')}",
            BaseArtifactType="Process Create"
        ))
        response.DisplayParams = (
            taskData.args.get_arg("path") + " " + " ".join(taskData.args.get_arg("args"))
        )
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
