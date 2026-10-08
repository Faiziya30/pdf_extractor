from fastapi import APIRouter, File, UploadFile

from app.controllers.document_controller import DocumentController
from app.schemas.document_schema import DocumentResponse, OutlineResponse, PagesResponse, ResourceResponse


def create_document_router(controller: DocumentController) -> APIRouter:
    router = APIRouter(prefix="/api/documents", tags=["documents"])

    @router.post("/upload", response_model=DocumentResponse)
    async def upload_document(file: UploadFile = File(...)):
        return await controller.upload(file)

    @router.get("/{document_id}", response_model=DocumentResponse)
    async def get_document(document_id: str):
        return controller.get(document_id).data

    @router.get("/{document_id}/pages", response_model=PagesResponse)
    async def get_pages(document_id: str):
        document = controller.get(document_id)
        return {"document_id": document_id, "pages": document.data["pages"]}

    @router.get("/{document_id}/outline", response_model=OutlineResponse)
    async def get_outline(document_id: str):
        document = controller.get(document_id)
        return {"document_id": document_id, "outline": document.data["outline"]}

    @router.delete("/{document_id}", response_model=ResourceResponse)
    async def delete_document(document_id: str):
        document = controller.get(document_id)
        summary = document.data["document"]
        controller.delete(document_id)
        return {"document": summary}

    return router