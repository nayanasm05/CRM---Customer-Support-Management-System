from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import AttachmentResponse
from app.services import attachment_service


router = APIRouter(
    tags=["Attachments"]
)


@router.post(
    "/tickets/{ticket_id}/attachments",
    response_model=AttachmentResponse
)
async def upload_attachment(
    ticket_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await attachment_service.create_attachment(
        db,
        ticket_id,
        file,
        current_user
    )


@router.get(
    "/tickets/{ticket_id}/attachments",
    response_model=list[AttachmentResponse]
)
def get_ticket_attachments(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return attachment_service.get_ticket_attachments(
        db,
        ticket_id,
        current_user
    )


@router.get("/attachments/{attachment_id}")
def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    attachment = attachment_service.get_attachment(
        db,
        attachment_id,
        current_user
    )

    return FileResponse(
        path=attachment.file_path,
        filename=attachment.file_name,
        media_type=attachment.file_type
    )


@router.delete("/attachments/{attachment_id}")
def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return attachment_service.delete_attachment(
        db,
        attachment_id,
        current_user
    )