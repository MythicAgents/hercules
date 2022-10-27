## Exercise 5 - Custom C2

### mythic.lab
This sequence of events happens on the linux `mythic.lab` host.

Eventually, our C2 profile is going to forward messages to Mythic, which means we need to remotely have the Mythic server available. We already did something similar with the `RabbitMQ` service earlier, so we're going to do the same sort of thing:

1. `sudo ./mythic-cli config set MYTHIC_SERVER_BIND_LOCALHOST_ONLY false`
2. `sudo ./mythic-cli restart`

### dev-desktop.lab
This sequence of events happens on the Windows `dev-desktop.lab` host.

It's often helpful in offensive engagements to have different kinds of C2 profiles. In Mythic, each C2 Profile does one thing - gets a message from somewhere to give to Mythic and put a message back somewhere for the agent to pick it up. The most common and simplist version of this is simply `http`:

* C2 Profile opens a port and listens for web traffic
* Agent connects and sends message
* C2 Profile relays message to Mythic (holding connection open)
* C2 Profile gets message from Mythic and replies to agent
* Connection closes

The `hercules` agent by default uses only `POST` http messages. For this exercise we're going to create a new C2 profile `hercules_c2` that only uses `GET` http messages instead. For simplicity sake, the `hercules_c2` is a clone of the `http` profile, just renamed. Our main modifications will come to the `hercules` agent itself.

1. `pip3 install mythic_c2_container`
2. `.\start_hercules_c2.ps1`
3. `.\start_hercules_exercise5.ps1`

You should now see a new C2 Profile show up in the Mythic UI.

## C2 Profile's server

Egress C2 Profiles have a `server*` binary. When you click to `start` a C2 Profile in the Mythic UI, the `mythic_service.py` program will spawn `server*` as a child process to handle the actual C2 communications piece. This `server*` binary can have any extension, it just has to start with `server` and live in the `c2_code` folder. For example, if it's just a python file that starts with `#!/usr/bin/env python3` then the system will process it as Python. You could just as easily call it `server.py` or make it an actual executable (make sure it matches your platform).

There are two main modifications to the `hercules_c2` profile from the `http` profile:
* The name of the profile changed in the `C:\hercules\C2_Profiles\hercules_c2\mythic\c2_functions\HerculesC2.py` file on line 11
* The value for the `Mythic` header in `C:\hercules\C2_Profiles\hercules_c2\c2_code\server` changed from `http` to `hercules_c2` on lines 85 and 95.

C2 Profiles must send a header called `Mythic` with their request to the Mythic server that has a value of their c2 profile name. This allows Mythic to get connections from any C2 Profile and easily trace it back to the appropriate encryption keys.

There's one more thing we need to specify as an environment variable for the `server*` process:

* `MYTHIC_ADDRESS=http://mythic.lab:17443/api/v1.4/agent_message`

This makes it easy for the `server*` process to redirect messages to Mythic since the endpoint might change over time. This is already set for you with the helper ps1 scripts for starting the c2 profile.

## Agent Side

We now need to update the agent to only do `GET` requests and track this as a separate profile.

The `C:\hercules\Payload_Type\hercules-Exercise5\agent_code\pkg\profiles` folder has a new `hercules_c2.go` file. This file is largely the same as the `http.go` file except that it performs a GET request instead of a POST request for all of its traffic.

1. Generate a new agent using `hercules_c2` and get a callback (either download and run the `exe` or get the UUID and encryption key and generate a new payload with `make`)

Notice how in the callback table and on the payloads table that it says the new `hercules_c2` profile name.