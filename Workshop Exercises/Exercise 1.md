## Exercise 1 - Remote Agent Development

### mythic.lab
This sequence of events happens on the Linux `mythic.lab` host.

In order to do remote agent development, we need to configure Mythic to allow us to remotely connect. By default, all of Mythic's services (except for the UI) listen on localhost (127.0.0.1), so remote development isn't possible without port forwarding. To make things easier, we can simply tell Mythic to not bind certain services to localhost:

1. 
```
sudo ./mythic-cli config set RABBITMQ_BIND_LOCALHOST_ONLY false
sudo ./mythic-cli config set MYTHIC_SERVER_BIND_LOCALHOST_ONLY false
```

We're specifically setting `RabbitMQ` and `mythic_server` to be available externally since that's how the various services within Mythic communicate. This opens up port `5672` and `17443` by default (but is adjustable). To apply this adjustment, we need to bring the container down and back up again, we can do this with the following:

2. `sudo ./mythic-cli restart`

There's one more thing we need from Mythic - the password for RabbitMQ so that our remote services can authenticate properly:

3. `sudo ./mythic-cli config get RABBITMQ_PASSWORD`

For the labs, we already set this so we don't need to worry about saving this.

### dev-desktop.lab
This sequence of events happens on the Windows `dev-desktop.lab` host.

Now that we have Mythic setup and ready for a remote agent, we need to create the environment and agent on our Windows host, `dev-desktop.lab`. For ease of use, all of these labs are hosted on GitHub (this is already cloned on your `C:\`):

1. `git clone https://github.com/MythicAgents/hercules`


To register an agent or c2 profile with Mythic, there's no need for Docker. Instead, all the functionality is based on a certain file/folder structure and the right PyPi package to handle the RabbitMQ communications.

For an agent, this PyPi package is [mythic_container](https://pypi.org/project/mythic-container/) version 0.2.11-rc05.

In an administrative PowerShell prompt, run:

2. `pip3 install mythic_container==0.2.11rc05`

In the `C:\hercules` folder there's a `requirements.txt` file which will allow you to install all the Python requirements for all the labs. This can all be installed via `pip3 install -r requirements.txt`. 

We then need a base instance of an agent to start with. Luckily, Mythic provides this. There's an entire base agent layout as part of ExampleContainers - [Example Containers](https://github.com/MythicMeta/ExampleContainers/tree/main/Payload_Type). 
If you want to start from this point in the future and not use the code here, you need to pick if you want to do the Mythic side of agent dev in Python or Golang and select the appropriate example container.  
For everybody doing the labs, we can simply move on to the next step since a base agent is already created for us.

#### For the lab

There's a series of steps below that are simplified for the labs - specifically getting the RabbitMQ password (we set it in Exercise 0 explicitly), updating the `rabbitmq_config.json` file, and starting the container.

3. `.\start_hercules_exercise1.ps1`

At this point you'll see output similar to :

```
INFO 2023-06-12 10:26:58,391 initialize  29  : [*] Using debug level: info
INFO 2023-06-12 10:26:58,391 start_services  365 : [+] Starting Services with version v1.0.7 and PyPi version 0.2.11-rc05

INFO 2023-06-12 10:26:58,391 start_services  386 : [*] Processing agent: hercules-exercise1
INFO 2023-06-12 10:26:58,391 GetConnection  90  : [*] Trying to connect to rabbitmq at: 127.0.0.1:5672
INFO 2023-06-12 10:26:58,400 GetConnection  104 : [+] Successfully connected to rabbitmq
INFO 2023-06-12 10:26:58,536 syncPayloadData  130 : [+] Successfully synced hercules-exercise1
INFO 2023-06-12 10:26:58,536 start_services  412 : [+] All services synced with Mythic!
INFO 2023-06-12 10:26:58,536 start_services  413 : [*] Starting services to listen...
INFO 2023-06-12 10:26:58,575 ReceiveFromMythicDirectExchange  256 : [*] started listening for messages on hercules-exercise1_payload_build
INFO 2023-06-12 10:26:58,585 ReceiveFromMythicDirectExchange  256 : [*] started listening for messages on hercules-exercise1_pt_task_create_tasking
INFO 2023-06-12 10:26:58,586 ReceiveFromMythicDirectExchange  256 : [*] started listening for messages on hercules-exercise1_pt_task_opsec_post_check
INFO 2023-06-12 10:26:58,588 ReceiveFromRPCQueue  295 : [*] started listening for messages on hercules-exercise1_pt_command_dynamic_query_function
INFO 2023-06-12 10:26:58,588 ReceiveFromMythicDirectExchange  256 : [*] started listening for messages on hercules-exercise1_pt_task_process_response
INFO 2023-06-12 10:26:58,589 ReceiveFromRPCQueue  295 : [*] started listening for messages on hercules-exercise1_mythic_rpc_other_service_rpc
INFO 2023-06-12 10:26:58,590 ReceiveFromMythicDirectExchange  256 : [*] started listening for messages on hercules-exercise1_pt_task_opsec_pre_check
INFO 2023-06-12 10:26:58,591 ReceiveFromMythicDirectExchange  256 : [*] started listening for messages on hercules-exercise1_pt_task_completion_function
INFO 2023-06-12 10:26:58,608 ReceiveFromRPCQueue  295 : [*] started listening for messages on hercules-exercise1_pt_rpc_resync

```

If you then go to the Mythic UI and click the headphone icon in the top left, you'll see your new agent, `hercules-exercise1` appear in the UI. 
Notice how the entire `hercules-Exericse1\agent_code` folder is empty - you don't need agent code to get the base agent service online, and Mythic doesn't track or care about what your actual agent code looks like.

That's the basis of hooking a new agent into Mythic. 

The general configuration and definition of your agent is located within the `hercules-Exercise1\agent_functions\builder.py`.

#### Outside the lab

3. `cd C:\hercules\Payload_Type\hercules-Exercise1`

There's one thing we need to configure here - the `rabbitmq_config.json` file needs two things from us - the password to authenticate to RabbitMQ and the hostname/IP of the RabbitMQ box (`mythic.lab`). We can get this password from the Mythic instance by either reading the `Mythic/.env` file or running `sudo ./mythic-cli config get RABBITMQ_PASSWORD`
ex:
```json
{
  "rabbitmq_password": "PqR9XJ957sfHqcxj6FsBMj4p",
  "rabbitmq_host": "mythic.lab",
  "mythic_host": "mythic.lab"
}
```

4. `python3 main.py`