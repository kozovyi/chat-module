from fastapi import Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from fastapi_users.authentication.transport.base import (
    Transport,
    TransportLogoutNotSupportedError,
)
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.schemas import model_dump


class BearerResponse(BaseModel):
    token_type: str
    access_token: str

class BearerResponseWithRefresh(BearerResponse):
    refresh_token: str


class BearerTransport(Transport):
    scheme: OAuth2PasswordBearer

    def __init__(self, tokenUrl: str):
        self.scheme = OAuth2PasswordBearer(tokenUrl, auto_error=False)

    async def get_login_response(self, access_token: str, refresh_token: str ) -> Response:
        bearer_response = BearerResponseWithRefresh(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

        return JSONResponse(model_dump(bearer_response))


    async def get_refresh_response(self, access_token: str, refresh_token: str) -> Response:
            bearer_response = BearerResponseWithRefresh(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
            return JSONResponse(model_dump(bearer_response))


    async def get_logout_response(self) -> Response:
        raise TransportLogoutNotSupportedError()

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {
            status.HTTP_200_OK: {
                "model": BearerResponseWithRefresh,
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "<ACCESS_TOKEN>",
                            "refresh_token": "<REFRESH_TOKEN>",
                            "token_type": "bearer",
                        }
                    }
                },
            },
        }

    @staticmethod
    def get_openapi_refresh_responses_success() -> OpenAPIResponseType:
        return {
            status.HTTP_200_OK: {
                "model": BearerResponseWithRefresh,
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "<NEW_ACCESS_TOKEN>",
                            "refresh_token": "<NEW_REFRESH_TOKEN>",
                            "token_type": "bearer",
                        }
                    }
                },
            },
        }

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        return {}





bearer_transport = BearerTransport(tokenUrl="/api/v1/auth/jwt/login")
