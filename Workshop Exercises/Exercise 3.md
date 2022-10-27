## Exercise 3 - Developing the Agent  

### dev-desktop.lab
This sequence of events happens on the Windows `dev-desktop.lab` host.

The `agent_code` section of `Payload_Type\hercules-Exercise3` now has code and the `builder.py` section of `Payload_Type\hercules-Exercise3\mythic` now has more substance. 

It's often helpful to a local build option as well as an automatic build option for agents. This allows a more generic way for agents to be built as well as a quick option for doing local development. For this lab, we'll be utilizing a `Makefile` to do our local build and test scenarios and a more complex `go build` command for doing it automatically through the Mythic UI.

When building locally, there are really only two things that your agent needs to get from Mythic:
1. Payload UUID - this is how Mythic is able to look up information about the payload
2. Cryptography Keys - this is how Mythic is able to properly encrypt/decrypt messages

Once you get these two things from Mythic (even after just creating a fake agent in the Mythic UI that fails to build), then you can plug them into your local build and make changesas necessary without worrying about the Mythic side of things.

In our example, the `Makefile` has a few parameters at the top including a `HTTP_UUID` variable and a `HTTP_AESPSK` variable. 

1. `.\start_hercules_exercise3.ps1`
2. In the Mythic UI, generate a new payload for `hercules-exercise3`. On the payloads screen, there's a blue `i` icon you can click to see metadata about the payload. From this screen, copy out the `UUID` and `Encryption Key` and edit them in the `Makefile`.
3. In another Powershell window, `cd C:\hercules\Payload_Type\hercules-Exercise3\agent_code`
4. `make build_and_run_http`
5. In the Mythic UI you should now see a new callback

We can edit anything in the `agent_code` folder without having to restart the `start_hercules_exercise3.ps1` program. You only need to restart that piece if something within the `mythic` folder changes. To show this:

1. Issue the `run` command in Mythic: `run c:\winnt\system32\cmd.exe /c whoami`
2. Wait for the agent to return output
3. Stop your running agent and modify the `agent_code\run\run.go` file on line `45` to add ` + "\nmodified code"`.
4. Run `make build_and_run_http` to get a new callback with your modified code
5. re-issue your task in the new callback, `run c:\winnt\system32\cmd.exe /c whoami`

Notice how your change was used without having to do anything with Mythic. The same thing is true even for a Docker-ized agent - the `agent_code` folder is mapped directly into the container, so changes don't require a container restart.