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