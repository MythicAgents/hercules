HTTP_UUID=16bb9575-9c0e-46fa-ab65-aff3c8334124
HTTP_CALLBACK_HOST=http://mythic.lab
HTTP_CALLBACK_PORT=80
HTTP_KILLDATE=2024-12-31
HTTP_CALLBACK_INTERVAL=5
HTTP_CALLBACK_JITTER=10
HTTP_POST_URI=data
HTTP_ENCRYPTED_EXCHANGE_CHECK=T
HTTP_AESPSK=
HTTP_PROXY_PORT=
HTTP_PROXY_USER=
HTTP_PROXY_HOST=
HTTP_GET_URI=data
HTTP_QUERY_NAME=q
HTTP_PROXY_BYPASS=False

BINARY_NAME=hercules
C2_HTTP=http
C2_HERCULES=hercules_c2
UseCustomC2Format=True

build_http:
	go build -o ${BINARY_NAME}_${C2_HTTP}.bin -tags="${C2_HTTP}" -ldflags=" \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.callback_host=${HTTP_CALLBACK_HOST}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.UUID=${HTTP_UUID}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.callback_port=${HTTP_CALLBACK_PORT}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.killdate=${HTTP_KILLDATE}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.callback_interval=${HTTP_CALLBACK_INTERVAL}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.callback_jitter=${HTTP_CALLBACK_JITTER}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.post_uri=${HTTP_POST_URI}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.encrypted_exchange_check=${HTTP_ENCRYPTED_EXCHANGE_CHECK}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.AESPSK=${HTTP_AESPSK}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.proxy_port=${HTTP_PROXY_PORT}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.proxy_user=${HTTP_PROXY_USER}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.proxy_host=${HTTP_PROXY_HOST}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.proxy_bypass=${HTTP_PROXY_BYPASS}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.UseCustomC2Format=${UseCustomC2Format}' \
" .

build_hercules_c2:
	go build -o ${BINARY_NAME}_${C2_HERCULES}.bin -tags="${C2_HERCULES}" -ldflags=" \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.callback_host=${HTTP_CALLBACK_HOST}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.UUID=${HTTP_UUID}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.callback_port=${HTTP_CALLBACK_PORT}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.killdate=${HTTP_KILLDATE}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.callback_interval=${HTTP_CALLBACK_INTERVAL}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.callback_jitter=${HTTP_CALLBACK_JITTER}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.post_uri=${HTTP_POST_URI}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.encrypted_exchange_check=${HTTP_ENCRYPTED_EXCHANGE_CHECK}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.AESPSK=${HTTP_AESPSK}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.proxy_port=${HTTP_PROXY_PORT}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.proxy_user=${HTTP_PROXY_USER}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.proxy_host=${HTTP_PROXY_HOST}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.proxy_bypass=${HTTP_PROXY_BYPASS}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.UseCustomC2Format=${UseCustomC2Format}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.get_uri=${HTTP_GET_URI}' \
-X 'github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/profiles.query_path_name=${HTTP_QUERY_NAME}' \
" .

run_http: 
	./${BINARY_NAME}_${C2_HTTP}.bin

run_hercules_c2:
	./${BINARY_NAME}_${C2_HERCULES}.bin

build_and_run_http: build_http run_http

build_and_run_hercules_c2: build_hercules_c2 run_hercules_c2

clean:
	go clean
	rm ${BINARY_NAME}_${C2_HTTP}.bin
	rm ${BINARY_NAME}_${C2_HERCULES}.bin