from mythic_container.MythicCommandBase import *
import json
import base64
import sys
from mythic_container.MythicRPC import *


class UploadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="remote_path",
                display_name="Remote Path",
                type=ParameterType.String,
                description="Path where the uploaded file will be written.",
                parameter_group_info=[
                    ParameterGroupInfo(ui_position=2, required=False)
                ],
            ),
            CommandParameter(
                name="file_id",
                display_name="File to Upload",
                type=ParameterType.File,
                description="The file to be written to the remote path.",
                parameter_group_info=[ParameterGroupInfo(ui_position=1)],
            ),
            CommandParameter(
                name="overwrite",
                display_name="Overwrite Exiting File",
                type=ParameterType.Boolean,
                description="Overwrite file if it exists.",
                default_value=False,
                parameter_group_info=[
                    ParameterGroupInfo(ui_position=3, required=False)
                ],
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary):
        self.load_args_from_dictionary(dictionary)


class UploadCommand(CommandBase):
    cmd = "upload"
    needs_admin = False
    help_cmd = "upload"
    description = "upload a file to the target."
    version = 1
    supported_ui_features = ["file_browser:upload"]
    author = "@xorrior"
    argument_class = UploadArguments
    attackmapping = ["T1020", "T1030", "T1041", "T1105"]
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
        try:
            file_resp = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
                TaskID=taskData.Task.ID,
                AgentFileID=taskData.args.get_arg("file")
            ))
            if file_resp.Success:
                if len(file_resp.Files) > 0:
                    original_file_name = file_resp.Files[0].Filename
                    if len(taskData.args.get_arg("remote_path")) == 0:
                        taskData.args.add_arg("remote_path", original_file_name)
                    elif taskData.args.get_arg("remote_path")[-1] == "/":
                        taskData.args.add_arg("remote_path", taskData.args.get_arg("remote_path") + original_file_name)
                    response.DisplayParams = f"{original_file_name} to {taskData.args.get_arg('remote_path')}"
                else:
                    raise Exception("Failed to find that file")
            else:
                raise Exception("Error from Mythic trying to get file: " + str(file_resp.Error))
        except Exception as e:
            raise Exception(
                "Error from Mythic: " + str(sys.exc_info()[-1].tb_lineno) + str(e)
            )
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
