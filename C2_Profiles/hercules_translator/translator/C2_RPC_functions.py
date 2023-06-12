import json
import base64
from mythic_container.TranslationBase import *


class herculesTranslator(TranslationContainer):
    name = "hercules_translator"
    description = "python translation service that does ROT1 on messages"
    author = "@its_a_feature_"

    async def translate_from_c2_format(self, inputMsg: TrCustomMessageToMythicC2FormatMessage) -> TrCustomMessageToMythicC2FormatMessageResponse:
        response = TrCustomMessageToMythicC2FormatMessageResponse(Success=True)
        if inputMsg.MythicEncrypts:
            base64Bytes = bytearray(inputMsg.Message)
            # our special sauce is to remove 1 from each byte
            for i in range(0, len(base64Bytes)):
                base64Bytes[i] = base64Bytes[i] - 1
            # print(base64Bytes)
            response.Message = json.loads(bytes(base64Bytes))
        else:
            response.Message = json.loads(inputMsg.Message)
        return response

    async def translate_to_c2_format(self, inputMsg: TrMythicC2ToCustomMessageFormatMessage) -> TrMythicC2ToCustomMessageFormatMessageResponse:
        response = TrMythicC2ToCustomMessageFormatMessageResponse(Success=True)

        if inputMsg.MythicEncrypts:
            jsonBytes = bytearray(json.dumps(inputMsg.Message).encode())
            for i in range(0, len(jsonBytes)):
                jsonBytes[i] = jsonBytes[i] + 1
            # print(jsonBytes)
            response.Message = bytes(jsonBytes)
        else:
            response.Message = base64.b64encode(
                inputMsg.UUID.encode() + json.dumps(inputMsg.Message).encode()
            )
        return response

    async def generate_keys(self, inputMsg: TrGenerateEncryptionKeysMessage) -> TrGenerateEncryptionKeysMessageResponse:
        response = TrGenerateEncryptionKeysMessageResponse(Success=True)
        response.DecryptionKey = b""
        response.EncryptionKey = b""
        return response
