function global:exit_agent {
    param($Job)
    exit
}
$Script:Management_Commands['exit_agent'] = 'exit_agent'