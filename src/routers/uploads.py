import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "uploads"

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post("/menu-image")
async def upload_menu_image(file: UploadFile = File(...)):
    """Upload a menu item image and return its public URL."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    extension = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }[file.content_type]

    filename = f"{uuid.uuid4().hex}{extension}"
    destination = UPLOAD_DIR / filename

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    destination.write_bytes(content)

    return {"url": f"/static/uploads/{filename}"}