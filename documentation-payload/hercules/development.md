+++
title = "Development"
chapter = false
weight = 20
pre = "<b>3. </b>"
+++

## Development Environment

For development, all you need is a text editor an a Windows host with PowerShell v5. We recommend Visual Studio Code or PowerShell ISE as the editor.

## Adding Commands

Command files are located in `hercules/agent_code` as `command.ps1`. There are two kinds of command files - those that are more management oriented and run within the general agent space, and pure tasking commands that execute within their own pshost space. 

A more management command example of of the following format:

```
function global:job_list {
    param($Job)
    try {
        $cur_jobs = $Script:Jobs | %{
            [pscustomobject]@{
                task_id = $_.task_id
                command = $_.command
                parameters = $_.parameters
                result = $_.result
                started = $_.started
                error = $_.error
                completed = $_.completed
            }
        }
        return [pscustomobject]@{
            completed = $true
            user_output = $cur_jobs | ConvertTo-Json
        } | ConvertTo-Json -Depth 4 -Compress
    }
    catch {
        return [pscustomobject]@{
            completed = $true
            user_output = $error[0] | Out-String
            status = "error"
        } | ConvertTo-Json -Depth 4 -Compress
    }
}
$Script:Management_Commands['job_list'] = 'job_list'
```

Notice where the command name `job_list` is located within there and that it returns JSON via PSObjects.

An example of a standard tasking command is as follows:

```
$Script:Commands.powershell = {
    function Start-Function { 
        param($Arguments)
        Invoke-Expression $Arguments
    }
}

```

This kind of command must always have `function Start-Function` with an argument of `$Arguments`.


To add a new command you need to create one of these two kinds of commands as `.ps1` files in `hercules/agent_code` and you also need to create the corresponding .py file in `hercules/mythic/agent_functions`.


## Adding C2 Profiles

Hercules currently only supports the HTTP profile. To add the ability for more profiles requires splitting out the basic HTTP get/post requests and adding in the required transports for new profiles. Ideally, you can abstract this away so that new profiles can be easily created and swaped in at creation time.
