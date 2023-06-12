#!/usr/bin/env python3

"""This is an example implementation of a C2 server that processes HTTP
communications with an Agent, performs routing with the Mythic server,
and adds the required Mythic header to the HTTP response to identify
the C2 profile forwarding the request.
"""
from sanic import Sanic
from sanic.response import html, redirect, text, raw
from sanic.exceptions import NotFound
import sys
import asyncio
import ssl
from pathlib import Path
import requests
import json
import os

config = {}


async def print_flush(message):
    """Print message and flush the stdout buffer.

    Python's stdout is buffered, so it collects data written
    into a buffer before it is written to the terminal. This
    forces the buffer to be written to the terminal instead of
    waiting for output to eventually occur.

    Args:
        message: self-explanatory
    """
    print(message)
    sys.stdout.flush()


def server_error_handler(request, exception):
    """Error handler for Sanic app. Formats server error to be presented.

    Args:
        request: object containing the HTTP request information
        exception: object containing exception information

    """
    if request is None:
        print("Invalid HTTP Method - Likely HTTPS trying to talk to HTTP")
        sys.stdout.flush()
        return html("Error: Failed to process request", status=500, headers={})
    return html(
        "Error: Requested URL {} not found".format(request.url),
        status=404,
        headers=config[request.app.name]["headers"],
    )


async def agent_message(request, **kwargs):
    """This is the route handler that processes a request from the Agent.

    Args:
        request: object containing the HTTP request information
        **kwargs: any additional arguments
    Returns:
        HTTP response object
    """
    global config
    try:
        if config[request.app.name]["debug"]:
            await print_flush(
                "agent_message request from: {} with {} and {}".format(
                    request.url, request.cookies, request.headers
                )
            )
            await print_flush(" and URI: {}".format(request.query_string))
        if config[request.app.name]["debug"]:
            await print_flush(
                "Forwarding along to: {}".format(config["mythic_address"])
            )
        if request.method == "POST":
            # manipulate the request if needed - change the "Mythic" header to match the name of your C2 profile
            response = requests.post(
                config["mythic_address"],
                data=request.body,
                verify=False,
                cookies=request.cookies,
                headers={"Mythic": "hercules_c2", **request.headers},
            )
        else:
            # manipulate the request if needed - change the "Mythic" header to match the name of your C2 profile
            # print(request.query_string)
            response = requests.get(
                config["mythic_address"] + "?{}".format(request.query_string),
                verify=False,
                data=request.body,
                cookies=request.cookies,
                headers={"Mythic": "hercules_c2", **request.headers},
            )
        return raw(
            response.content,
            headers=config[request.app.name]["headers"],
            status=response.status_code,
        )
    except Exception as e:
        if request is None:
            await print_flush(
                "Invalid HTTP Method - Likely HTTPS trying to talk to HTTP"
            )
            return server_error_handler(request, e)
        if config[request.app.name]["debug"]:
            await print_flush("error in agent_message: {}".format(str(e)))
        return server_error_handler(request, e)


if __name__ == "__main__":
    # sys.path.append("/Mythic/mythic")
    from mythic_container.C2ProfileBase import *

    config_file = open("config.json", "rb")
    main_config = json.loads(config_file.read().decode("utf-8"))
    print("Opening config and starting instances...")
    sys.stdout.flush()
    # basic mapping of the general endpoints to the real endpoints
    try:
        config["mythic_address"] = os.environ["MYTHIC_ADDRESS"]
    except Exception as e:
        print("failed to find MYTHIC_ADDRESS environment variable")
        sys.stdout.flush()
        sys.exit(1)
    # now look at the specific instances to start
    for inst in main_config["instances"]:
        config[str(inst["port"])] = {
            "debug": inst["debug"],
            "headers": inst["ServerHeaders"],
        }
        if inst["debug"]:
            print(
                "Debugging statements are enabled. This gives more context, but might be a performance hit"
            )
        else:
            print("Debugging statements are disabled")
        sys.stdout.flush()
        # now to create an app instance to handle responses
        app = Sanic(str(inst["port"]))
        app.config["REQUEST_MAX_SIZE"] = 1000000000
        app.config["REQUEST_TIMEOUT"] = 600
        app.config["RESPONSE_TIMEOUT"] = 600
        app.add_route(agent_message, "/<uri:path>", methods=["GET", "POST"])
        app.add_route(agent_message, "/", methods=["GET", "POST"])
        app.error_handler.add(Exception, server_error_handler)
        keyfile = Path(inst["key_path"])
        certfile = Path(inst["cert_path"])
        if keyfile.is_file() and certfile.is_file():
            context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(inst["cert_path"], keyfile=inst["key_path"])
            if inst["debug"]:
                server = app.create_server(
                    host="0.0.0.0",
                    port=inst["port"],
                    ssl=context,
                    debug=False,
                    return_asyncio_server=True,
                    access_log=True,
                )
            else:
                server = app.create_server(
                    host="0.0.0.0",
                    port=inst["port"],
                    ssl=context,
                    debug=False,
                    return_asyncio_server=True,
                    access_log=False,
                )
            if inst["debug"]:
                print("using SSL for port {}".format(inst["port"]))
                sys.stdout.flush()
        else:
            if inst["debug"]:
                print("not using SSL for port {}".format(inst["port"]))
                sys.stdout.flush()
            if inst["debug"]:
                server = app.create_server(
                    host="0.0.0.0",
                    port=inst["port"],
                    debug=False,
                    return_asyncio_server=True,
                    access_log=True,
                )
            else:
                server = app.create_server(
                    host="0.0.0.0",
                    port=inst["port"],
                    debug=False,
                    return_asyncio_server=True,
                    access_log=False,
                )
        task = asyncio.ensure_future(server)

    try:
        loop = asyncio.get_event_loop()

        def callback(fut):
            try:
                fetch_count = fut.result()
            except:
                print("port already in use")
                sys.stdout.flush()
                sys.exit()

        task.add_done_callback(callback)
        loop.run_forever()
    except:
        sys.exit()
        loop.stop()
