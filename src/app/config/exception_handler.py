from typing import Awaitable, Callable
from fastapi import HTTPException, Request
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
            if (isinstance(exception, HTTPException)):
                http_exception = exception
                message = {"mensagem": f"{http_exception.detail}"}
                print("Error: ", http_exception)
                return JSONResponse(message, http_exception.status_code)
            else:
                print("Error: ", exception)
                return JSONResponse({"mensagem": f"Erro interno da API, por favor tente mais tarde." }, 500)
