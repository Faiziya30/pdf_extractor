import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.controllers.document_controller import DocumentController
from app.exceptions.document_exceptions import DocumentError
from app.routes.document_routes import create_document_router
from app.utils.response_utils import error_payload

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="SmartPDF API", version="1.0.0")
allowed_origins = {settings.frontend_url, "http://127.0.0.1:5173"}
app.add_middleware(CORSMiddleware, allow_origins=list(allowed_origins), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
document_controller = DocumentController()
app.include_router(create_document_router(document_controller))


@app.get("/api/health")
async def health():
    return {"success": True, "message": "SmartPDF API is running"}


@app.exception_handler(DocumentError)
async def document_error_handler(_: Request, exc: DocumentError):
    return JSONResponse(status_code=exc.status_code, content=error_payload(exc.code, exc.message))


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(_: Request, __: RequestValidationError):
    return JSONResponse(status_code=422, content=error_payload("VALIDATION_ERROR", "The request did not contain a valid PDF file."))


@app.exception_handler(Exception)
async def unexpected_error_handler(_: Request, exc: Exception):
    logger.exception("Unexpected server error: %s", exc)
    return JSONResponse(status_code=500, content=error_payload("INTERNAL_ERROR", "An unexpected server error occurred."))