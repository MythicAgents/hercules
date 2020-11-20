from PayloadBuilder import *
import asyncio
import os
from distutils.dir_util import copy_tree
import tempfile
import base64

# Icons made by "https://www.flaticon.com/authors/freepik" "Freepik"

class MyNewAgent(PayloadType):

    name = "hercules" 
    file_extension = "ps1"
    author = "@Airzero24"
    supported_os = [  
        SupportedOS.Windows
    ]
    wrapper = False  
    wrapped_payloads = []  
    note = "This payload uses PowerShell to create a simple agent for demonstration purposes"
    supports_dynamic_loading = True
    build_parameters = {
        "output": BuildParameter(
            name="output",
            parameter_type=BuildParameterType.ChooseOne,
            description="Choose output format",
            choices=["ps1", "base64"],
        )
    }
    c2_profiles = ["HTTP"]
    support_browser_scripts = [
        BrowserScript(script_name="create_table", author="@its_a_feature_")
    ]

    async def build(self) -> BuildResponse:
        # this function gets called to create an instance of your payload
        resp = BuildResponse(status=BuildStatus.Success)
        # create the payload
        try:
            command_code = ""
            for cmd in self.commands.get_commands():
                command_code += (
                    open(self.agent_code_path / "{}.ps1".format(cmd), "r").read() + "\n"
                )
            base_code = open(
                self.agent_code_path / "base_agent.ps1", "r"
            ).read()
            base_code = base_code.replace("UUID_HERE", self.uuid)
            base_code = base_code.replace("COMMANDS_HERE", command_code)
            for c2 in self.c2info:
                profile = c2.get_c2profile()["name"]
                for key, val in c2.get_parameters_dict().items():
                    base_code = base_code.replace(key, val)
            if self.get_parameter("output") == "base64":
                    resp.payload = base64.b64encode(base_code.encode())
                    resp.set_message("Successfully Built")
                    resp.status = BuildStatus.Success
            else:
                resp.payload = base_code.encode()
                resp.message = "Successfully built!"
        except Exception as e:
            resp.set_status(BuildStatus.Error)
            resp.set_message("Error building payload: " + str(e))
        return resp
