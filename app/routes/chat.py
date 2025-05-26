from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest
from app.services.graph import run_graph_with_message
from app.memory.store import session_exists

router = APIRouter()

@router.post("/chat")
async def chat(req: ChatRequest):
    # Validate session
    if not session_exists(req.session_id):
        raise HTTPException(
            status_code=400,
            detail="Session not found. Please upload a PDF first."
        )

    try:
        # Run the LangGraph flow
        response = run_graph_with_message(req.session_id, req.message)
        # response= "Hii!"
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while processing chat: {str(e)}"
        )