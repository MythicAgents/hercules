from mythic_payloadtype_container.PayloadBuilder import *
from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import asyncio
import os
import json


class Hercules(PayloadType):
    name = "hercules-exercise1"
    file_extension = "exe"
    author = "@xorrior, @djhohnstein, @Ne0nd0g, @its_a_feature_"
    supported_os = [SupportedOS.Linux, SupportedOS.MacOS, SupportedOS.Windows]
    wrapper = False
    wrapped_payloads = []
    note = "A test small agent for Mythic Workshops"
    supports_dynamic_loading = False
    mythic_encrypts = True
    build_parameters = [
        BuildParameter(
            name="architecture",
            parameter_type=BuildParameterType.ChooseOne,
            description="Choose the agent's architecture ",
            choices=["AMD_x64", "ARM_x64"],
            default_value="AMD_x64",
        ),
    ]
    c2_profiles = ["http", "hercules_c2"]
    translation_container = None  # "hercules_translator" # None

    async def build(self) -> BuildResponse:
        # this function gets called to create an instance of your payload
        resp = BuildResponse(status=BuildStatus.Success)
        return resp
