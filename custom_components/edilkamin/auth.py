import json
import logging
import asyncio
from datetime import datetime, timedelta

import async_timeout
import aiohttp
from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)


class Auth:
    """Class to make authenticated requests."""

    amazon_cognito = "https://cognito-idp.eu-central-1.amazonaws.com/"
    payload = '{"UserContextData":{"EncodedData":"eyJwYXlsb2FkIjoie1widXNlcm5hbWVcIjpcIjBiZDgwMTI3LTM3YWQtNDQ4Yi1hNDg3LTNlNDc0YjAwMDE4MFwiLFwiY29udGV4dERhdGFcIjp7XCJDYXJyaWVyXCI6XCJPcmFuZ2UgQlwiLFwiQXBwbGljYXRpb25WZXJzaW9uXCI6XCIxLjIuOS03M1wiLFwiSGFzU2ltQ2FyZFwiOlwidHJ1ZVwiLFwiUGhvbmVUeXBlXCI6XCJpUGhvbmUxMiwzXCIsXCJEZXZpY2VJZFwiOlwiODA2Yzk4ZjYtZDdkMy00ZGMwLTk2ZGQtOTI4NzRlNWVkZTM1XCIsXCJOZXR3b3JrVHlwZVwiOlwiQ1RSYWRpb0FjY2Vzc1RlY2hub2xvZ3lMVEVcIixcIlNjcmVlbldpZHRoUGl4ZWxzXCI6XCIxMTI1XCIsXCJQbGF0Zm9ybVwiOlwiaU9TXCIsXCJTY3JlZW5IZWlnaHRQaXhlbHNcIjpcIjI0MzZcIixcIkFwcGxpY2F0aW9uVGFyZ2V0U2RrXCI6XCI5MDAwMFwiLFwiQXBwbGljYXRpb25OYW1lXCI6XCJjb20uZWRpbGthbWluLnRoZW1pbmRcIixcIkRldmljZU9zUmVsZWFzZVZlcnNpb25cIjpcIjE1LjQuMVwiLFwiRGV2aWNlRmluZ2VycHJpbnRcIjpcIkFwcGxlXFxcL2lQaG9uZVxcXC9pUGhvbmUxMiwzXFxcLy06MTUuNC4xXFxcLy1cXFwvLTotXFxcL3JlbGVhc2VcIixcIlRoaXJkUGFydHlEZXZpY2VJZFwiOlwiNzY3NjkzNjgtMUZDMS00QjQ5LTk2QjctMkRGMEFEQUQzOTVEXCIsXCJEZXZpY2VMYW5ndWFnZVwiOlwiZnItQkVcIixcIkNsaWVudFRpbWV6b25lXCI6XCIrMDI6MDBcIixcIkJ1aWxkVHlwZVwiOlwicmVsZWFzZVwiLFwiRGV2aWNlTmFtZVwiOlwiaVBob25lIEFsZXhpc1wifSxcInVzZXJQb29sSWRcIjpcImV1LWNlbnRyYWwtMV9CWW1RMlZCbG9cIixcInRpbWVzdGFtcFwiOlwiMTY1MDIxNDk5Mjk0NlwifSIsInZlcnNpb24iOiJJT1MyMDE3MTExNCIsInNpZ25hdHVyZSI6IkJBNTRxNmdldjhZMUVyZmh1TG9pNGNrSEFIRzIrVjVwRmlNTmc0SUxVMVk9In0="},"AuthParameters":{"REFRESH_TOKEN":"eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.HbY9oViZ2J0PivepBTEHaOhu1vrpj_1IacLNOQ1z0fjpr0NkK85w5Dd54Wes45Fng3sa_xCMf3L8rfXA1Tk61ZGX4trWX-XByhxgJIWavdje2l_QJVB6iMeEhsFa4MGAxuU32ohlr1c1k2Pjk5yAecZp3WkLkLG0-TcMuS6vULxhfiRTFXZwJirYcHzrxGoFyyuUQ0VyK1nkL6WivWRByG-bdXv2-6xP62ebMWU00NsiIL15tYx8y6LomxHf5bRzJG_sdu4T_3zSHy_0YkZNTrVDaExiEC4t5Uyd1fYcD-kIkz7S9DW5PQBIP2LmIRphZpsHaxwdUPefnpdF4TRlew.Khkjm-TijT7y2pBr.m0Fu5AA0dZLC7nM8MIlZpX0RdRYV6gcfoKFpTtp4fjAfYNbfy8bxHDgHj4LegWA5vWEJZ_9lCHyQRmL87b6gObFZYKdQrbpSvzkqnZJYDusY9dskN5-YGQiK6zbcL7ihM4jo_M3BTgWq3H5pQdQ3b36OgSFG0g4Wpn-M67z4hVpL11dfDJHf12jiDpHX0lXYJbAWzlpE7goNE69urQYe8htsr7eBlQSWZGMpA_9VcxwxLogM2heucK5pJnSHsewMYn0tORpW8LT8g02cV_6-WyRlYu2-c_b57H0MQzK2N4p1qAMLkXpWqvCx-oZ7cHrLGewC7nIbaQ9-p65W1vGVJ1E5ObLZNiI_yjMrQGPGAiHhuRUO0D3saKs88p2FSI9nKQh67sNa-V3lEInfuslNtmNP4gRvc3pzH06bQ414iSgzx0TfaK62si9hmzC3oq-p_YwMMCC97CrF954MhQhdzWMfYEGI_CLklh3TIp6NIjvk7F-_tkAirjbmZgIgenxYrV_o5BQxXzo2p_g-B3WOm5V1j0dGnHmcu-R-E-IZjaVllrorjyKzO3xsq6P4t6agZgFWHagu_1jPzakcCE37NhSxdrt9_xVTjFktkzJyq4zCQZ9FEU2PoMGxhpImWOltdfmS_a7AWaCbqIFqeWdWgjpT-Xji1KrBfo9syWe-xDdnVYoft6WxWp0ts7KVN1belmqeM0-P19oW-giFeuCuYCFWf0-EipoaBs7oTuMwVszKgaisiAVkUAogTyYd445hhww11abap5735uXYcX6i-HOwqzvLoEEr_IdC2NmQda2pmKDB_FMuQfBAfDBAfbiT9op2hQAIPphrsQei2yCkUnJmUhJCYD4OvftiX5VfyvoUHpqybHOfwg6vT6UdweoxeqW_eZCLilN6cXg0asDUF7B0oRx98JmXn7q9eAqon68PSkr3xrtqbW5rvbZxcVfBI7t77MZ9ByMQlrLb3ozAY2geFC9RNBQaqXUYSzd0fDm9yoxbA07HWwzEOOW8iEREhxmA0j5_VmR_b_hxcgseJ0qgDnrxyyl8i1Q3NhkX0ivtPzPZA0VXyqmX9JubL1CTJDRUzqDENOZV0jWFnJyVRhxf72Ap7OPwoXCOHav8-sDsdFfv3V-GjKrdhNbch6hRl16kTkxlkT8jcFzHsEO60kBdh5eNfI46_2mQV1mBvfVX_2mdT0ksxEoXuTCHGDzM0KuPjoPIlvd10707NY1F8heIJiampqP477TAtvIOMTpQZ1zyblHGLTvph9r5KdCkwe5cAg1dCIPJWmMKQfKRSU12DSdqFD3PVm3mn_QayrImcNc8aOHrvLM-haprQJIHyGR0.XOPrLRHzePBRr_EeG8iu4w"},"AuthFlow":"REFRESH_TOKEN_AUTH","ClientId":"7sc1qltkqobo3ddqsk4542dg2h"}'
    headers = {
        "content-type": "application/x-amz-json-1.1",
        "x-amz-target": "AWSCognitoIdentityProviderService.InitiateAuth",
    }

    def __init__(self, websession: ClientSession):
        """Initialize the auth."""
        self.access_token = None
        self.expires_in = datetime.now()
        self.websession = websession

    async def get_token(self):

        if datetime.now() < self.expires_in:
            _LOGGER.debug("Get access token cached, refrehs token after %s", self.expires_in)
            return self.access_token
        try:
            _LOGGER.debug("Get access token")
            response = await self.websession.request(
                "POST", self.amazon_cognito, headers=self.headers, data=self.payload
            )
            data = await response.text()
            data = json.loads(data)
            self.access_token = data.get("AuthenticationResult").get("AccessToken")
            expires_in = data.get("AuthenticationResult").get("ExpiresIn")
            self.expires_in = datetime.now() + timedelta(seconds=expires_in)

            return self.access_token
        except aiohttp.ClientError as error:
            _LOGGER.error("Error connecting to Edilkamin API: %s", error)
        except asyncio.TimeoutError as error:
            _LOGGER.debug("Timeout connecting to Edilkamin API: %s", error)

        return None
