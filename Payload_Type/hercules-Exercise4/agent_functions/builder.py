from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import asyncio
import os
import json

# Enable additional message details to the Mythic UI
debug = True


class Hercules(PayloadType):
    name = "hercules-exercise4"
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
            choices=["AMD_x64"],
            default_value="AMD_x64",
        ),
    ]
    build_steps = [
        BuildStep(step_name="Configuring", step_description="Stamping in configuration values"),
        BuildStep(step_name="Compiling...", step_description="Compiling agent")
    ]
    c2_profiles = ["http"]
    agent_path = pathlib.Path("") / "agent_functions"
    agent_code_path = pathlib.Path("") / "agent_code"
    agent_icon_path = pathlib.Path("") / "agent_functions" / "hercules.svg"
    translation_container = "hercules_translator" # None

    async def build(self) -> BuildResponse:
        resp = BuildResponse(status=BuildStatus.Error)
        target_os = "linux"
        if self.selected_os == "macOS":
            target_os = "darwin"
        elif self.selected_os == "Windows":
            target_os = "windows"
        if len(self.c2info) != 1:
            resp.build_stderr = "hercules only accepts one c2 profile at a time"
            return resp
        try:
            agent_build_path = os.path.abspath(str(self.agent_code_path))

            # Get the selected C2 profile information (e.g., http or websocket)
            c2 = self.c2info[0]
            profile = c2.get_c2profile()["name"]
            if profile not in self.c2_profiles:
                resp.build_message = "Invalid c2 profile name specified"
                return resp

            # This package path is used with Go's "-X" link flag to set the value string variables in code at compile
            # time. This is how each profile's configurable options are passed in.
            hercules_repo_profile = f"github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles"

            # Build Go link flags that are passed in at compile time through the "-ldflags=" argument
            # https://golang.org/cmd/link/
            ldflags = f"-s -w -X '{hercules_repo_profile}.UUID={self.uuid}' "
            if self.translation_container is not None:
                ldflags += f"-X '{hercules_repo_profile}.UseCustomC2Format=True' "
            # Iterate over the C2 profile parameters and associated variable through Go's "-X" link flag
            for key, val in c2.get_parameters_dict().items():
                # dictionary instances will be crypto components
                if key == "AESPSK":
                    ldflags += f" -X '{hercules_repo_profile}.{key}={val['enc_key']}' "
                elif key == "headers":
                    #v = json.dumps(val).replace('"', '\`"')
                    #ldflags += f" -X '{hercules_repo_profile}.{key}={v}'"
                    pass
                else:
                    if val:
                        ldflags += f" -X '{hercules_repo_profile}.{key}={val}' "
            # Set the Go -buildid argument to an empty string to remove the indicator
            ldflags += " -buildid="
            goarch = "amd64"
            if self.get_parameter("architecture") == "ARM_x64":
                goarch = "arm64"
            command = ""
            if target_os == "windows":
                command += f" set GOOS={target_os}&& set GOARCH={goarch}&& "
            else:
                command += f" GOOS={target_os} GOARCH={goarch} "
            command += f'go build -tags="{profile}" -ldflags="{ldflags}" -o hercules-{target_os}'
            await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                PayloadUUID=self.uuid,
                StepName="Configuring",
                StepStdout=f"New build command:\n{command}",
                StepSuccess=True
            ))
            # Execute the constructed xgo command to build Poseidon
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=agent_build_path,
            )

            # Collect and data written Standard Output and Standard Error
            stdout, stderr = await proc.communicate()
            if stdout:
                resp.build_stdout += f"\n[STDOUT]\n{stdout.decode()}"
                if debug:
                    resp.build_message += f"\n[BUILD]{command}\n"
            if stderr:
                resp.build_stderr += f"\n[STDERR]\n{stderr.decode()}"
                if debug:
                    resp.build_stderr += f"\n[BUILD]{command}\n"
            output_path = os.path.join(agent_build_path, f"hercules-{target_os}")
            if os.path.exists(output_path):
                resp.payload = open(output_path, "rb").read()
                os.remove(output_path)
            else:
                resp.build_stderr += f"{output_path} does not exist"
                resp.status = BuildStatus.Error
                await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                    PayloadUUID=self.uuid,
                    StepName="Compiling...",
                    StepStdout=f"build errors:\n{resp.build_stderr}",
                    StepSuccess=False
                ))
                return resp

            # Successfully created the payload without error
            resp.build_message += (
                f"\nCreated Hercules payload!\n"
                f"OS: {target_os}, "
                f"C2 Profile: {profile}\n[BUILD]{command}\n"
            )
            await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                PayloadUUID=self.uuid,
                StepName="Compiling...",
                StepStdout=f"build output:\n{resp.build_stdout}",
                StepSuccess=True
            ))
            resp.status = BuildStatus.Success
            return resp
        except Exception as e:
            resp.build_stderr += "\n" + str(e)
        return resp
