from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json


class SleepArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="jitter",
                type=ParameterType.Number,
                description="Jitter percentage.",
                default_value=-1,
                parameter_group_info=[
                    ParameterGroupInfo(ui_position=2, required=False)
                ],
            ),
            CommandParameter(
                name="interval",
                type=ParameterType.Number,
                description="Sleep time in seconds",
                default_value=-1,
                parameter_group_info=[ParameterGroupInfo(ui_position=1)],
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            try:
                self.load_args_from_json_string(self.command_line)
            except:
                pieces = self.command_line.split(" ")
                if len(pieces) == 1:
                    self.add_arg("interval", pieces[0])
                elif len(pieces) == 2:
                    self.add_arg("interval", pieces[0])
                    self.add_arg("jitter", pieces[1])
                else:
                    raise Exception("Wrong number of arguments. should be 1 or 2")
        else:
            raise Exception("Missing arguments for sleep")

    async def parse_dictionary(self, dictionary):
        self.load_args_from_dictionary(dictionary)


class SleepCommand(CommandBase):
    cmd = "sleep"
    needs_admin = False
    help_cmd = "sleep {interval} [jitter%]"
    description = "Update the sleep interval for the agent."
    version = 1
    author = "@xorrior"
    argument_class = SleepArguments
    attackmapping = []
    supported_ui_features = ["callback_table:sleep"]
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
        response.DisplayParams = str(taskData.args.get_arg("interval")) + "s"
        if taskData.args.get_arg("jitter") >= 0:
            response.DisplayParams += " with " + str(taskData.args.get_arg("jitter")) + "% jitter"
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        await SendMythicRPCCallbackUpdate(MythicRPCCallbackUpdateMessage(
            TaskID=task.Task.ID,
            SleepInfo=response,
        ))
        return resp
