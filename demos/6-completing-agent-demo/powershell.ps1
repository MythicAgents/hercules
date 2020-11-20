$Script:Commands.powershell = {
    function Start-Function { 
        param($Arguments)
        Invoke-Expression $Arguments
    }
}
