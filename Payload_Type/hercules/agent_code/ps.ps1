$Script:Commands.ps = {
    function Start-Function {
        param($Arguments)
        Add-Type -MemberDefinition @"
[DllImport("kernel32.dll", SetLastError = true, CallingConvention = CallingConvention.Winapi)]
[return: MarshalAs(UnmanagedType.Bool)]
public static extern bool IsWow64Process(
    [In] System.IntPtr hProcess,
    [Out, MarshalAs(UnmanagedType.Bool)] out bool wow64Process);
"@ -Name NativeMethods -Namespace Kernel32
        $ps = Get-Process -IncludeUserName
        $is32Bit = [int]0
        $output = $ps | %{
            [pscustomobject]@{
                process_id = $_.Id
                architecture = (&{if ([Kernel32.NativeMethods]::IsWow64Process($_.handle, [ref]$is32Bit) -and $is32Bit) {"x86"} else {"x64"}})
                name = $_.name
                user = $_.username
                bin_path = $_.path
                parent_process_id = ''
            }
        }
        return [pscustomobject]@{
            completed = $true
            user_output = $output | ConvertTo-Json
        } | ConvertTo-Json -Depth 4 -Compress
    }
}
