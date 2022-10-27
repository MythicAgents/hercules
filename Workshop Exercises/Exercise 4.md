## Exercise 4 - Custom Message Formats  

### dev-desktop.lab
This sequence of events happens on the Windows `dev-desktop.lab` host.

Mythic uses JSON for its messages since it's generally universal, but that doesn't mean that it's absolutely universal. Some languages have native support while others require libraries that might bloat agents. Some developers might want binary formats or completely custom formats to make things harder for defenders to analyze. 

It's not practical to make every agent developer fully knowledgeable about the Mythic back-end, just like it's not practical for the Mythic back-end to support a bunch of different formats. Instead, Mythic has the idea of a `translation container` that acts as an intermediary for non-standard formats.

There's an example translation container available for this exercise at `C:\hercules\C2_Profiles\hercules_translator`. Translation containers act very similarly to C2 Profiles in that they're responsible for one specific thing - translation. The reason they're split out from both C2 Profiles and Agents though is that it's entirely possible for sombody to make a message format (like Type-Length-Value) that they want to leverage in more than one agent. So, this information needs to be in a more commonly accessible format.

Translation containers are pretty simple - they offer 3 functions:
* `translate_from_c2_format` - convert from special format to JSON
* `translate_to_c2_format` - convert from JSON to special format
* `generate_keys` - allow developers to use their own cryptography rather than the standard AES256_HMAC that Mythic uses by providing a function to generate their own encryption/decryption keys. 

#### What does this flow look like?
{{<mermaid>}}
sequenceDiagram
    participant T as Translation Container
    participant M as Mythic
    participant C as C2 Profile Container
    participant A as Agent
    A ->>+ C: Agent Sends Message
    C ->>+ M: C2 Forwards to Mythic
    Note over M: Start Processing Message
    M ->> M: Base64 Decode and fetch UUID
    M ->>+ T: Send to Translator
    T ->> T: Decrypt Message
    T ->> T: Translate To Mythic JSON
    T -->>- M: Return JSON Message
    M ->> M: Process Message
    M ->> M: Process Delegates
    Note over M: Stop Processing Message
    M ->> M: Create Response
    M ->>+ T: Send to Translator
    T ->> T: Translate to Custom Format
    T ->> T: Encrypt Message
    T -->>- M: Return Final Blob
    M -->>- C: Return Final Blob
    C -->>- A: Return Final Message
{{< /mermaid >}}

We can start this translation container in the following way:

1. `pip3 install mythic_translator_container`
2. `.\start_hercules_translator.ps1`

You should now see a new section in the UI when you click on the `headphones` icon in the top left specifically for translation containers. You'll notice though that it's not associated with anything yet. We need to associate these two things together in our `builder.py` file.

Just like how we define which `c2 profiles` the agent supports within the `builder.py` file, we also define which `translation container` we need to leverage. This is already set up for you, so we can simply start the `hercules-exercise4` agent container:

1. `.\start_hercules_exercise4.ps1`

You should now see the new `hercules-exercise4` agent available and the translation container should be updated to indicate that it's associated with this agent.

This is a custom message format though, so we need to update our agent to not speak JSON, but to speak the custom format (JSON + ROT1). This is already added into the agent, we just need to update our local `Makefile` for the `hercules-Exercise4`:

1. Update the configuration `UseCustomC2Format=False` to `UseCustomC2Format=True`
2. Make a payload within the UI for the new `hercules-exercise4` agent.
3. Update the `HTTP_UUID` and `HTTP_AESPSK` in the Makefile to match the new agent
4. `make build_and_run_http`

You should now see a new callback appear in the UI - this payload is now utilizing the translation container.
