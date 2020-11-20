function global:set_sleep {
    param($Job)
    try {
        $data = $Job.parameters | ConvertFrom-Json
        if ($data.sleep.GetType().Name -eq "Int32") {
            $Agent.Sleep = $data.sleep
            if ($data.Properties.Name -contains "jitter"){
                if ($data.jitter.GetType().Name -eq "Int32") {
                    $Agent.Jitter = $data.jitter
                }
            }
            return [pscustomobject]@{
                completed = $true
                user_output = "Sleep successfully updated"
            } | ConvertTo-Json -Depth 4 -Compress
        }
        else {
            return [pscustomobject]@{
                completed = $true
                user_output = "Sleep could not be updated"
                status = "error"
            } | ConvertTo-Json -Depth 4 -Compress
        }
    }
    catch {
        return [pscustomobject]@{
            completed = $true
            user_output = $error[0] | Out-String
            status = "error"
        } | ConvertTo-Json -Depth 4 -Compress
    }
}
$Script:Management_Commands['set_sleep'] = 'set_sleep'

