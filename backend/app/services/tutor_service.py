from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.tutor import TutorRepository
from app.DTOs.tutor import ChatRequest, ChatResponse, TutorSessionResponse
from app.services.agent.graph import agent_app
from typing import List

class TutorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TutorRepository(db)
        from app.repositories.document import DocumentRepository
        self.doc_repo = DocumentRepository(db)

    def get_history(self, user_id: int) -> List[TutorSessionResponse]:
        sessions = self.repo.get_user_sessions(user_id)
        return [TutorSessionResponse.model_validate(s) for s in sessions]

    def get_session(self, session_id: str, user_id: int) -> TutorSessionResponse:
        session = self.repo.get_session(session_id, user_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return TutorSessionResponse.model_validate(session)

    def create_empty_session(self, user_id: int) -> TutorSessionResponse:
        session = self.repo.create_session(user_id, "New Conversation")
        return TutorSessionResponse.model_validate(session)

    def delete_session(self, session_id: str, user_id: int):
        success = self.repo.delete_session(session_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"detail": "Session deleted"}

    def delete_all_sessions(self, user_id: int):
        count = self.repo.delete_all_sessions(user_id)
        return {"detail": f"Deleted {count} sessions"}

    def rename_session(self, session_id: str, user_id: int, new_title: str) -> TutorSessionResponse:
        session = self.repo.rename_session(session_id, user_id, new_title)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return TutorSessionResponse.model_validate(session)

    async def chat(self, request: ChatRequest, user_id: int) -> ChatResponse:
        session_id = request.session_id
        
        # 1. Create or validate session
        if not session_id:
            title = request.question[:30] + "..." if len(request.question) > 30 else request.question
            session = self.repo.create_session(user_id, title, document_id=request.document_id)
            session_id = str(session.id)
        else:
            session = self.repo.get_session(session_id, user_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")

        # 2. Extract chat history (Limited to last 10 messages to prevent unlimited context)
        chat_history = []
        for msg in session.messages[-10:]:
            content = msg.content or (msg.structured_data.get('content', '') if msg.structured_data else '')
            chat_history.append({"role": msg.role, "content": content})
            
        # 3. Save user message
        user_msg = self.repo.add_message(session_id, role="user", content=request.question)

        # Get all allowed documents for the user
        user_docs = self.doc_repo.get_by_owner_id(user_id)
        allowed_document_ids = [str(d.id) for d in user_docs]
        document_names = {str(d.id): d.filename for d in user_docs}

        # 4. Call LangGraph agent
        print("[TUTOR] Request started")
        inputs = {
            "original_question": request.question,
            "document_id": str(session.document_id) if session.document_id else "",
            "chat_history": chat_history,
            "allowed_document_ids": allowed_document_ids,
            "document_names": document_names
        }
        final_state = await agent_app.ainvoke(inputs)
        answer_dict = final_state.get("answer", {})
        
        # answer_dict should be {"content": "...", "citations": [...]}
        content_text = answer_dict.get("content", "")
        
        # 5. Save AI message
        ai_msg = self.repo.add_message(session_id, role="ai", content=content_text, structured_data=answer_dict)

        return ChatResponse(
            session_id=session_id,
            user_message=user_msg,
            ai_message=ai_msg
        )

    async def chat_stream(self, request: ChatRequest, user_id: int):
        import asyncio
        import json
        
        session_id = request.session_id
        
        # 1. Create or validate session
        if not session_id:
            title = request.question[:30] + "..." if len(request.question) > 30 else request.question
            session = self.repo.create_session(user_id, title, document_id=request.document_id)
            session_id = str(session.id)
        else:
            session = self.repo.get_session(session_id, user_id)
            if not session:
                yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
                return

        # 2. Extract chat history
        chat_history = []
        for msg in session.messages[-10:]:
            content = msg.content or (msg.structured_data.get('content', '') if msg.structured_data else '')
            chat_history.append({"role": msg.role, "content": content})
            
        # 3. Save user message immediately with image data if present
        user_structured_data = {}
        if request.image_data:
            user_structured_data["image"] = request.image_data
            
        user_msg = self.repo.add_message(session_id, role="user", content=request.question, structured_data=user_structured_data if user_structured_data else None)
        
        stream_queue = asyncio.Queue()

        # Get all allowed documents for the user
        user_docs = self.doc_repo.get_by_owner_id(user_id)
        allowed_document_ids = [str(d.id) for d in user_docs]
        document_names = {str(d.id): d.filename for d in user_docs}

        # 4. Run LangGraph agent
        print("[TUTOR] Request started")
        inputs = {
            "original_question": request.question,
            "document_id": str(session.document_id) if session.document_id else "",
            "chat_history": chat_history,
            "stream_queue": stream_queue,
            "image_data": request.image_data,
            "allowed_document_ids": allowed_document_ids,
            "document_names": document_names
        }
        
        task = asyncio.create_task(agent_app.ainvoke(inputs))
        
        # 5. Yield chunks as they arrive
        while not task.done():
            try:
                chunk = await asyncio.wait_for(stream_queue.get(), timeout=0.1)
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            except asyncio.TimeoutError:
                continue
                
        # Drain remaining queue
        while not stream_queue.empty():
            chunk = stream_queue.get_nowait()
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
        # 6. Save final response and yield complete block
        try:
            final_state = task.result()
            answer_dict = final_state.get("answer", {})
            content_text = answer_dict.get("content", "")
            
            ai_msg = self.repo.add_message(session_id, role="ai", content=content_text, structured_data=answer_dict)
            
            final_response = ChatResponse(
                session_id=session_id,
                user_message=user_msg,
                ai_message=ai_msg
            )
            yield f"data: {json.dumps({'done': True, 'response': final_response.model_dump(mode='json')})}\n\n"
        except Exception as e:
            error_str = str(e)
            print(f"[TUTOR] Gemini request failed: {error_str}")
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Quota exceeded" in error_str:
                error_str = "Google Gemini API rate limit exceeded. The free tier allows a limited number of requests per minute. Please wait about a minute and try again."
            yield f"data: {json.dumps({'error': error_str})}\n\n"
