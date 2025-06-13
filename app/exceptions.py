"""
Módulo de exceções para a API de Astrologia.
Centraliza o tratamento de exceções e handlers personalizados.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

class AstroAPIException(Exception):
    """Exceção base para erros da API de Astrologia."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

def add_exception_handlers(app: FastAPI):
    """
    Adiciona handlers de exceção personalizados à aplicação FastAPI.
    
    Args:
        app: Instância da aplicação FastAPI
    """
    @app.exception_handler(AstroAPIException)
    async def astro_api_exception_handler(request: Request, exc: AstroAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        # Log da exceção para depuração
        print(f"Erro não tratado: {type(exc).__name__}: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Erro interno do servidor"}
        )
