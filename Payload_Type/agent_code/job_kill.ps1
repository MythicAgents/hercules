function global:job_kill {
    param($Job)
    try {
        $index = 0..($Script:Jobs.Count -1) | Where { $Script:Jobs[$_].task_id -eq $Job.parameters }
        $Script:Jobs[$index].result = "Killed by job_kill"
        $Script:Jobs[$index].completed = $true
        $user_output = "Killed target PS Session"
        $Script:Jobs[$index].pshost.Dispose()
        return [pscustomobject]@{
            completed = $true
            user_output = $user_output
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
$Script:Management_Commands['job_kill'] = 'job_kill'
