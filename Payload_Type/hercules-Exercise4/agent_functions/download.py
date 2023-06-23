from mythic_container.MythicCommandBase import *
import json


class DownloadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise Exception("Must provide path to thing to download")
        try:
            # if we get JSON, it's from the file browser, so adjust accordingly
            tmp_json = json.loads(self.command_line)
            self.command_line = tmp_json["path"] + "/" + tmp_json["file"]
        except:
            # if it wasn't JSON, then just process it like a normal command-line argument
            pass


class DownloadCommand(CommandBase):
    cmd = "download"
    needs_admin = False
    help_cmd = "download /remote/path/to/file"
    description = "Download a file from the target."
    version = 1
    supported_ui_features = ["file_browser:download", "callback_table:download"]
    author = "@xorrior"
    argument_class = DownloadArguments
    attackmapping = ["T1020", "T1030", "T1041"]
    browser_script = BrowserScript(
        script_name="download_new", author="@djhohnstein", for_new_ui=True
    )
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
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
