from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import os
from app.services.rag_service import RAGService, INDEX_DIR
from app.auth.security import require_admin

router = APIRouter()
rag = RAGService()

@router.post("/rag/ingest")
async def rag_ingest(file: UploadFile = File(...), current_user=Depends(require_admin)):
	try:
		os.makedirs(INDEX_DIR, exist_ok=True)
		target = os.path.join(INDEX_DIR, file.filename)
		with open(target, "wb") as f:
			f.write(await file.read())
		count = rag.ingest_pdf(target)
		return {"ok": True, "chunks": count}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@router.get("/rag/status")
def rag_status(current_user=Depends(require_admin)):
	return rag.status()
