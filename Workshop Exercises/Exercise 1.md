## Exercise 1 - Remote Agent Development

### mythic.lab
This sequence of events happens on the Linux `mythic.lab` host.

In order to do remote agent development, we need to configure Mythic to allow us to remotely connect. By default, all of Mythic's services (except for the UI) listen on localhost (127.0.0.1), so remote development isn't possible without port forwarding. To make things easier, we can simply tell Mythic to not bind certain services to localhost:

1. `sudo ./mythic-cli config set RABBITMQ_BIND_LOCALHOST_ONLY false`

We're specifically setting `RabbitMQ` to be available externally since that's how the various services within Mythic communicate. This opens up port `5672` by default (but is adjustable). To apply this adjustment, we need to bring the container down and back up again, we can do this with the following:

2. `sudo ./mythic-cli restart`

There's one more thing we need from Mythic - the password for RabbitMQ so that our remote services can authenticate properly:

3. `sudo ./mythic-cli config get RABBITMQ_PASSWORD`

For the labs, we already set this so we don't need to worry about saving this.

### dev-desktop.lab
This sequence of events happens on the Windows `dev-desktop.lab` host.

Now that we have Mythic setup and ready for a remote agent, we need to create the environment and agent on our Windows host, `dev-desktop.lab`. For ease of use, all of these labs are hosted on GitHub (this is already cloned on your `C:\`):

1. `git clone https://github.com/MythicAgents/hercules`


To register an agent or c2 profile with Mythic, there's no need for Docker. Instead, all of the functionality is based on a certain file/folder structure and the right PyPi package to handle all of the RabbitMQ communications.

For an agent, this PyPi package is [mythic_payloadtype_container](https://pypi.org/project/mythic-payloadtype-container/) version 0.1.18.

In an administrative PowerShell prompt, run:

2. `pip3 install mythic_payloadtype_container==0.1.18`

In the `C:\hercules` folder there's a `requirements.txt` file which will allow you to install all of the Python requirements for all of the labs. This can all be installed via `pip3 install -r requirements.txt`. 

We then need a base instance of an agent to start with. Luckily, Mythic provides this. There's an entire base agent layout as part of Mythic - [Example Payload Type](https://github.com/its-a-feature/Mythic/tree/master/Example_Payload_Type). If you want to start from this point in the future, all you need to do is modify the `name` of the agent (https://github.com/its-a-feature/Mythic/blob/master/Example_Payload_Type/mythic/agent_functions/builder.py#L10) here before moving on to the next step. For everybody doing the labs, we can simply move on to the next step since a base agent is already created for us.

#### For the lab

There's a series of steps below that are simplified for the labs - specifically getting the RabbitMQ password (we set it in Exercise 0 explicitly), updating the `rabbitmq_config.json` file, and starting the container.

3. `.\start_hercules_exercise1.ps1`

At this point you'll see output similar to :

```
[*] To enable debug logging, set `MYTHIC_ENVIRONMENT` variable to `testing`
[*] Mythic PayloadType Version: 12
[*] PayloadType PyPi Version: 0.1.18
[*] Setting hostname (which should match payload type name exactly) to: hercules-exercise1
[*] Trying to connect to rabbitmq at: 192.168.53.151:5672
[*] mythic_service - Waiting for messages in mythic_service with version 12.
[*] mythic_service - total instances of hercules-exercise1 container running: 1
[+] Ready to go!
```

If you then go to the Mythic UI and click the headphone icon in the top left, you'll see your new agent, `hercules-exercise1` appear in the UI. Notice how the entire `hercules-Exericse1\agent_code` folder is empty - you don't need agent code to get the base agent service online, and Mythic doesn't track or care about what your actual agent code looks like.

That's the basis of hooking a new agent into Mythic. 

The general configuration and definition of your agent is located within the `hercules-Exercise1\mythic\agent_functions\builder.py`.

#### Outside the lab

3. `cd C:\hercules\Payload_Type\hercules-Exercise1\mythic`

There's one thing we need to configure here - the `rabbitmq_config.json` file needs two things from us - the password to authenticate to RabbitMQ and the hostname/IP of the RabbitMQ box (`mythic.lab`). We can get this password from the Mythic instance by either reading the `Mythic/.env` file or running `sudo ./mythic-cli config get RABBITMQ_PASSWORD`
ex:
```json
{
  "password": "PqR9XJ957sfHqcxj6FsBMj4p",
  "host": "mythic.lab"
}
```

4. `python3 mythic_service.py`