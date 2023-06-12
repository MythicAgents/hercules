$env:MYTHIC_ADDRESS="http://mythic.lab:17443/api/v1.4/agent_message"
$env:MYTHIC_HOST="mythic.lab"
$env.MYTHIC_PORT=17443
$env.RABBITMQ_HOST="mythic.lab"
Start-Process -FilePath "$env:comspec" -ArgumentList "/k python mythic_service.py" -WorkingDirectory ".\C2_Profiles\hercules_c2\mythic"