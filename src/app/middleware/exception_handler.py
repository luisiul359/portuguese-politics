from typing import Awaitable, Callable
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            response = await call_next(request)

            if (response.status_code == 404):
                return JSONResponse({"mensagem": f"Endpoint: /{request.url.path} não existe."}, response.status_code)
            return response
        except Exception as exception:
            message_error = {"mensagem": f"Erro interno da API, por favor tente mais tarde." }
            if (isinstance(exception, KeyError)):
                return JSONResponse(message_error, 500)
            else:
                return JSONResponse(message_error, 500)
