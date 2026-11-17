"""
Chat API Endpoint: Interacts with the Supervisor Orchestrator, logs to DB,
handles state persistence and safety audits.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.database import get_db
from app.models.schema import User, Session, Message, SafetyAudit
from app.models.pydantic_models import ChatMessageRequest, ChatMessageResponse
from app.agents.supervisor import SupervisorOrchestrator
from app.agents.state import ConversationState
from app.memory.true_memory import TrueMemoryService
from app.memory.vector_search import VectorSearchService

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(request: ChatMessageRequest, db: AsyncSession = Depends(get_db)):
    # 1. Resolve or Create User
    user_res = await db.execute(select(User).where(User.id == request.user_id))
    user = user_res.scalar_one_or_none()
    if not user:
        user = User(id=request.user_id, region=request.region)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # 2. Resolve or Create Session
    session_id = request.session_id
    current_mode = request.mode_override or "GUIDED_CBT"
    session_obj = None

    if session_id:
        s_res = await db.execute(select(Session).where(Session.id == session_id))
        session_obj = s_res.scalar_one_or_none()

    if not session_obj:
        session_obj = Session(user_id=user.id, mode=current_mode)
        db.add(session_obj)
        await db.commit()
        await db.refresh(session_obj)
        session_id = session_obj.id

    if request.mode_override:
        session_obj.mode = request.mode_override
        await db.commit()

    # 3. Retrieve Confirmed Memories Semantically if Privacy Mode is OFF
    relevant_memories = []
    if not user.privacy_mode_enabled:
        mems = await TrueMemoryService.get_user_memories(db, user.id, status="CONFIRMED")
        raw_memories = [{"category": m.category, "content": m.content, "status": m.status} for m in mems]
        # Semantic vector ranking based on user message
        relevant_memories = VectorSearchService.rank_memories(
            query_text=request.content,
            memories=raw_memories,
            top_k=2,
            similarity_threshold=0.35
        )

    # 4. Save User Message
    user_msg = Message(
        session_id=session_id,
        sender="USER",
        content=request.content
    )
    db.add(user_msg)
    await db.commit()

    # 5. Execute Supervisor State Machine
    supervisor = SupervisorOrchestrator(region=user.region)
    state = ConversationState(
        session_id=session_id,
        user_id=user.id,
        current_mode=session_obj.mode,
        user_message=request.content,
        relevant_memories=relevant_memories
    )
    
    updated_state = supervisor.process_turn(state)

    # 6. Safety Audit Log if flagged
    if updated_state.safety_halt:
        audit = SafetyAudit(
            session_id=session_id,
            user_id=user.id,
            raw_input=request.content,
            risk_level="CRITICAL",
            risk_score=1.0,
            gate_triggered="SAFETY_ORCHESTRATOR",
            category="CRISIS_INTERRUPT",
            action_taken="EMERGENCY_RESOURCES_DISPLAYED"
        )
        db.add(audit)

    # 7. Persist Proposed Memories to DB
    persisted_proposals = []
    if not user.privacy_mode_enabled:
        for prop in updated_state.proposed_memories:
            saved_mem = await TrueMemoryService.create_proposed_memory(
                db=db,
                user_id=user.id,
                category=prop["category"],
                content=prop["content"],
                confidence_score=prop["confidence_score"],
                source_type=prop["source_type"]
            )
            if saved_mem:
                persisted_proposals.append({
                    "id": saved_mem.id,
                    "category": saved_mem.category,
                    "content": saved_mem.content,
                    "confidence_score": saved_mem.confidence_score,
                    "confirmation_prompt": prop.get("confirmation_prompt", "")
                })

    # 8. Save AI Response Message
    bot_msg = Message(
        session_id=session_id,
        sender="NIVARA",
        content=updated_state.agent_response,
        metadata_payload={
            "mode": updated_state.current_mode,
            "distortions": updated_state.detected_distortions,
            "rubric_score": updated_state.clinical_rubric_score
        }
    )
    db.add(bot_msg)
    await db.commit()

    return ChatMessageResponse(
        session_id=session_id,
        reply=updated_state.agent_response,
        sender="NIVARA",
        mode=updated_state.current_mode,
        is_crisis=updated_state.safety_halt,
        crisis_payload=updated_state.safety_payload,
        detected_distortions=updated_state.detected_distortions,
        proposed_memories=persisted_proposals,
        suggested_quick_replies=updated_state.quick_replies
    )

