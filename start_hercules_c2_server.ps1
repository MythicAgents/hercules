$env:MYTHIC_ADDRESS="http://mythic.lab:17443/api/v1.4/agent_message"
Start-Process -FilePath "$env:comspec" -ArgumentList "/k python server.py" -WorkingDirectory ".\C2_Profiles\hercules_c2\c2_code"