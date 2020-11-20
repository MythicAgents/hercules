from PayloadBuilder import *
import asyncio
import os
from distutils.dir_util import copy_tree
import tempfile
import base64

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

    async def build(self) -> BuildResponse:
        # this function gets called to create an instance of your payload
        resp = BuildResponse(status=BuildStatus.Success)
        return resp
