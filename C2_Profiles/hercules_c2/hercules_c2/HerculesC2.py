"""This file configures the C2 parameters to be used by a payload for communications.

Mythic will utilize the defined class inheriting C2Profile to identify the C2 profile
and parameters that are presented to the operator in the payload creation UI. These
parameters are added to the payload's PayloadType (builder.py) so they can be used
during the build process.
"""
from mythic_container.C2ProfileBase import *
import json
import pathlib


class HerculesC2(C2Profile):
    name = "hercules_c2"
    description = "Uses HTTP(S) connections with a simple query parameter or basic POST messages. For more " \
                  "configuration options use dynamicHTTP."
    author = "@its_a_feature_"
    is_p2p = False
    is_server_routed = False
    server_folder_path = pathlib.Path(".") / "c2_code"
    server_binary_path = server_folder_path / "server.py"
    parameters = [
        C2ProfileParameter(
            name="callback_port",
            description="Callback Port",
            default_value="80",
            verifier_regex="^[0-9]+$",
            required=False,
        ),
        C2ProfileParameter(
            name="killdate",
            description="Kill Date",
            parameter_type=ParameterType.Date,
            default_value=365,
            required=False,
        ),
        C2ProfileParameter(
            name="encrypted_exchange_check",
            description="Perform Key Exchange",
            choices=["T", "F"],
            required=False,
            parameter_type=ParameterType.ChooseOne,
        ),
        C2ProfileParameter(
            name="callback_jitter",
            description="Callback Jitter in percent",
            default_value="23",
            verifier_regex="^[0-9]+$",
            required=False,
        ),
        C2ProfileParameter(
            name="headers",
            description="HTTP Headers",
            required=False,
            parameter_type=ParameterType.Dictionary,
            default_value=[
                {
                    "name": "User-Agent",
                    "max": 1,
                    "default_value": "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",
                    "default_show": True,
                },
                {
                    "name": "Host",
                    "max": 1,
                    "default_value": "",
                    "default_show": False,
                },
                {
                    "name": "*",
                    "max": -1,
                    "default_value": "",
                    "default_show": False
                }
            ]
        ),
        C2ProfileParameter(
            name="AESPSK",
            description="Crypto type",
            default_value="aes256_hmac",
            parameter_type=ParameterType.ChooseOne,
            choices=["aes256_hmac", "none"],
            required=False,
            crypto_type=True
        ),
        C2ProfileParameter(
            name="callback_host",
            description="Callback Host",
            default_value="https://domain.com",
            verifier_regex="^(http|https):\/\/[a-zA-Z0-9]+",
        ),
        C2ProfileParameter(
            name="get_uri",
            description="GET request URI (don't include leading /)",
            default_value="index",
            required=False,
        ),
        C2ProfileParameter(
            name="post_uri",
            description="POST request URI (don't include leading /)",
            default_value="data",
            required=False,
        ),
        C2ProfileParameter(
            name="query_path_name",
            description="Name of the query parameter for GET requests",
            default_value="q",
            required=False,
            verifier_regex="^[^\/]",
        ),
        C2ProfileParameter(
            name="proxy_host",
            description="Proxy Host",
            default_value="",
            required=False,
            verifier_regex="^$|^(http|https):\/\/[a-zA-Z0-9]+",
        ),
        C2ProfileParameter(
            name="proxy_port",
            description="Proxy Port",
            default_value="",
            verifier_regex="^$|^[0-9]+$",
            required=False,
        ),
        C2ProfileParameter(
            name="proxy_user",
            description="Proxy Username",
            default_value="",
            required=False,
        ),
        C2ProfileParameter(
            name="proxy_pass",
            description="Proxy Password",
            default_value="",
            required=False,
        ),
        C2ProfileParameter(
            name="callback_interval",
            description="Callback Interval in seconds",
            default_value="10",
            verifier_regex="^[0-9]+$",
            required=False,
        ),
    ]

    async def opsec(self, inputMsg: C2OPSECMessage) -> C2OPSECMessageResponse:
        """Check payload's C2 configuration for OPSEC issues

        :param inputMsg: Payload's C2 Profile configuration
        :return: C2OPSECMessageResponse detailing the results of the OPSEC check
        """
        response = C2OPSECMessageResponse(Success=True)

        # perform OPSEC checks against the parameters. In this example, the callback port
        # is checked against common HTTPS ports when the callback host contains "https"
        params = inputMsg.Parameters
        if "https" in params["callback_host"] and params["callback_port"] not in [
            "443",
            "8443",
            "7443",
        ]:
            response.Success = False
            response.Message = f"Mismatch - HTTPS specified, but port {params['callback_port']}, is not one of the standard port (443, 8443)\n",
        else:
            response.Message = "Basic OPSEC checks passed\n"
        return response

    async def config_check(self, inputMsg: C2ConfigCheckMessage) -> C2ConfigCheckMessageResponse:
        """Check a payload's C2 configuration to see if it matches the local configuration

        :param inputMsg: Payload's C2 Profile configuration
        :return: C2ConfigCheckMessageResponse detailing the results of the configuration check
        """
        response = C2ConfigCheckMessageResponse(Success=True)
        try:
            with open("./c2_code/config.json") as f:
                config = json.load(f)
                possible_ports = []
                for inst in config["instances"]:
                    possible_ports.append(
                        {"port": inst["port"], "use_ssl": inst["use_ssl"]}
                    )
                    if str(inst["port"]) == str(inputMsg.Parameters["callback_port"]):
                        if (
                                "https" in inputMsg.Parameters["callback_host"]
                                and not inst["use_ssl"]
                        ):
                            message = f"C2 Profile container is configured to NOT use SSL on port {inst['port']}, but the callback host for the agent is using https, {inputMsg.Parameters['callback_host']}.\n\n"
                            message += "This means there should be the following connectivity for success:\n"
                            message += f"Agent via SSL to {inputMsg.Parameters['callback_host']} on port {inst['port']}, then redirection to C2 Profile container WITHOUT SSL on port {inst['port']}"
                            response.Success = False
                            response.Error = message
                            return response
                        elif (
                                "https" not in inputMsg.Parameters["callback_host"]
                                and inst["use_ssl"]
                        ):
                            message = f"C2 Profile container is configured to use SSL on port {inst['port']}, but the callback host for the agent is using http, {inputMsg.Parameters['callback_host']}.\n\n"
                            message += "This means there should be the following connectivity for success:\n"
                            message += f"Agent via NO SSL to {inputMsg.Parameters['callback_host']} on port {inst['port']}, then redirection to C2 Profile container WITH SSL on port {inst['port']}"
                            response.Message = message
                            return response
                        else:
                            message = f"C2 Profile container and agent configuration match port, {inst['port']}, and SSL expectations.\n"
                            response.Message = message
                            return response
                message = f"Failed to find port, {inputMsg.Parameters['callback_port']}, in C2 Profile configuration\n"
                message += f"This could indicate the use of a redirector, or a mismatch in expected connectivity.\n\n"
                message += (
                    f"This means there should be the following connectivity for success:\n"
                )
                if "https" in inputMsg.Parameters["callback_host"]:
                    message += f"Agent via HTTPS on port {inputMsg.Parameters['callback_port']} to {inputMsg.Parameters['callback_host']} (should be a redirector).\n"
                else:
                    message += f"Agent via HTTP on port {inputMsg.Parameters['callback_port']} to {inputMsg.Parameters['callback_host']} (should be a redirector).\n"
                if len(possible_ports) == 1:
                    message += f"Redirector then forwards request to C2 Profile container on port, {possible_ports[0]['port']}, {'WITH SSL' if possible_ports[0]['use_ssl'] else 'WITHOUT SSL'}"
                else:
                    message += f"Redirector then forwards request to C2 Profile container on one of the following ports: {json.dumps(possible_ports)}\n"
                if "https" in inputMsg.Parameters["callback_host"]:
                    message += f"\nAlternatively, this might mean that you want to do SSL but are not using SSL within your C2 Profile container.\n"
                    message += f"To add SSL to your C2 profile:\n"
                    message += f"\t1. Go to the C2 Profile page\n"
                    message += f"\t2. Click configure for the http profile\n"
                    message += f"\t3. Change 'use_ssl' to 'true' and make sure the port is {inputMsg.Parameters['callback_port']}\n"
                    message += f"\t4. Click to stop the profile and then start it again\n"
                response.Message = message
                return response
        except Exception as e:
            response.Success = False
            response.Error = str(e)
            return response

    async def redirect_rules(self, inputMsg: C2GetRedirectorRulesMessage) -> C2GetRedirectorRulesMessageResponse:
        """Generate Apache ModRewrite rules given the Payload's C2 configuration

        :param inputMsg: Payload's C2 Profile configuration
        :return: C2GetRedirectorRulesMessageResponse detailing some Apache ModRewrite rules for the payload
        """
        response = C2GetRedirectorRulesMessageResponse(Success=True)
        # This example generates Apache mod_rewrite rules for Mythic C2 profiles
        # to redirect non-C2 traffic to another site.
        output = "#mod_rewrite rules generated from @AndrewChiles' project https://github.com/threatexpress/mythic2modrewrite:\n"
        # Get User-Agent
        errors = ""
        ua = ""
        uris = []
        if "headers" in inputMsg.Parameters:
            for header in inputMsg.Parameters["headers"]:
                if header["key"] == "User-Agent":
                    ua = header["value"]
        else:
            errors += "[!] User-Agent Not Found\n"
        # Get all profile URIs
        if "get_uri" in inputMsg.Parameters:
            uris.append("/" + inputMsg.Parameters["get_uri"])
        else:
            errors += "[!] No GET URI found\n"
        if "post_uri" in inputMsg.Parameters:
            uris.append("/" + inputMsg.Parameters["post_uri"])
        else:
            errors += "[!] No POST URI found\n"
        # Create UA in modrewrite syntax. No regex needed in UA string matching, but () characters must be escaped
        ua_string = ua.replace("(", "\(").replace(")", "\)")
        # Create URI string in modrewrite syntax. "*" are needed in regex to support GET and uri-append parameters on the URI
        uris_string = ".*|".join(uris) + ".*"

        address = "C2_SERVER_HERE"
        c2_rewrite_template = """RewriteRule ^.*$ "{c2server}%{{REQUEST_URI}}" [P,L]"""
        c2_rewrite_output = []
        with open("./c2_code/config.json") as f:
            config = json.load(f)
            for inst in config["instances"]:
                c2_rewrite_output.append(
                    c2_rewrite_template.format(
                        c2server=f"https://{address}:{inst['port']}"
                        if inst["use_ssl"]
                        else f"http://{address}:{inst['port']}"
                    )
                )

        htaccess_template = """
    ########################################
    ## .htaccess START
    RewriteEngine On
    ## C2 Traffic (HTTP-GET, HTTP-POST, HTTP-STAGER URIs)
    ## Logic: If a requested URI AND the User-Agent matches, proxy the connection to the Teamserver
    ## Consider adding other HTTP checks to fine tune the check.  (HTTP Cookie, HTTP Referer, HTTP Query String, etc)
    ## Refer to http://httpd.apache.org/docs/current/mod/mod_rewrite.html
    ## Only allow GET and POST methods to pass to the C2 server
    RewriteCond %{{REQUEST_METHOD}} ^(GET|POST) [NC]
    ## Profile URIs
    RewriteCond %{{REQUEST_URI}} ^({uris})$
    ## Profile UserAgent
    RewriteCond %{{HTTP_USER_AGENT}} "{ua}"
    {c2servers}
    ## Redirect all other traffic here
    RewriteRule ^.*$ {redirect}/? [L,R=302]
    ## .htaccess END
    ########################################
        """
        htaccess = htaccess_template.format(
            uris=uris_string,
            ua=ua_string,
            c2servers="\n".join(c2_rewrite_output),
            redirect="redirect",
        )
        output += "#\tReplace 'redirect' with the http(s) address of where non-matching traffic should go, ex: https://redirect.com\n"
        output += f"\n{htaccess}"
        if errors != "":
            response.Success = False
            response.Error = errors
            return response
        else:
            response.Message = output
            return response
