from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.services.agent.state import AgentState
from app.services.qdrant_service import QdrantService
from app.services.embedding import EmbeddingService
from app.config.config import settings
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

class TutorResponse(BaseModel):
    content: str = Field(description="The main markdown conversational response.")

def get_llm():
    if settings.AI_PROVIDER == "gemini":
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
            return None
        return "gemini-native"
    else:
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "YOUR_REAL_OPENAI_API_KEY" or settings.OPENAI_API_KEY == "sk-placeholder-replace-with-real-key":
            return None
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(temperature=0, api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini")

async def understand_question(state: AgentState) -> AgentState:
    """Initializes state variables."""
    print("--- UNDERSTANDING QUESTION ---")
    return {
        "search_query": state.get("original_question", ""),
        "retrieval_attempts": 0,
        "context": [],
        "citations": [],
        "answer": ""
    }

async def decide_retrieval(state: AgentState) -> AgentState:
    """Uses LLM to decide if we need to search the vector DB."""
    print("--- DECIDING RETRIEVAL ---")
    
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get('chat_history', [])])
    
    llm = get_llm()
    if llm is None:
        q_lower = state["original_question"].lower()
        if any(word in q_lower for word in ["document", "pdf", "uploaded", "according to", "context"]):
            return {"require_retrieval": True}
        return {"require_retrieval": False}
        
    if llm == "gemini-native":
        # Bypass Gemini LLM call to save API rate limits
        q_lower = state["original_question"].lower()
        if any(word in q_lower for word in ["document", "pdf", "uploaded", "according to", "context"]):
            return {"require_retrieval": True}
        return {"require_retrieval": False}
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a routing assistant. Decide if the user's latest input requires searching a knowledge base of university documents. Respond ONLY with 'yes' or 'no'."),
        ("user", "Conversation History:\n{history}\n\nLatest Question: {question}")
    ])
    chain = prompt | llm
    response = await chain.ainvoke({"question": state["original_question"], "history": history_str})
    
    require_retrieval = "yes" in str(response.content).strip().lower()
    return {"require_retrieval": require_retrieval}

async def rewrite_query(state: AgentState) -> AgentState:
    """Rewrites the query to optimize for vector search."""
    print(f"--- REWRITING QUERY (Attempt {state.get('retrieval_attempts', 0) + 1}) ---")
    
    llm = get_llm()
    if llm is None:
        return {"search_query": state["original_question"], "retrieval_attempts": state.get("retrieval_attempts", 0) + 1}
    
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get('chat_history', [])])
    
    if llm == "gemini-native":
        # Bypass Gemini LLM call to save API rate limits
        return {
            "search_query": state["original_question"],
            "retrieval_attempts": state.get("retrieval_attempts", 0) + 1
        }
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert at optimizing search queries for vector databases. Rewrite the user's question into a concise keyword-rich query, taking into account the conversation history. Do not include any conversational text."),
        ("user", "Conversation History:\n{history}\n\nOriginal question: {question}\nPrevious search query (if any): {prev_query}\nWrite an optimized search query:")
    ])
    chain = prompt | llm
    response = await chain.ainvoke({
        "question": state["original_question"], 
        "prev_query": state.get("search_query", ""),
        "history": history_str
    })
    
    return {
        "search_query": str(response.content).strip(),
        "retrieval_attempts": state.get("retrieval_attempts", 0) + 1
    }

async def retrieve_context(state: AgentState) -> AgentState:
    """Searches Qdrant for context."""
    print(f"--- RETRIEVING CONTEXT FOR: {state['search_query']} ---")
    emb_service = EmbeddingService()
    embeddings = await emb_service.generate_embeddings([state["search_query"]])
    
    document_id = str(state.get("document_id")) if state.get("document_id") else None
    allowed_document_ids = state.get("allowed_document_ids")

    # 3. Retrieve from Qdrant
    qdrant = QdrantService()
    results = qdrant.search_embeddings(
        query_vector=embeddings[0], 
        limit=5, 
        document_id=document_id,
        allowed_document_ids=allowed_document_ids
    )
    
    return {"context": results}

async def check_context_quality(state: AgentState) -> AgentState:
    """Grades the retrieved context to see if it answers the question."""
    print("--- CHECKING CONTEXT QUALITY ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a grader. Read the provided context and the user's question. Does the context contain enough information to answer the question? Respond ONLY with 'good' or 'poor'."),
        ("user", "Question: {question}\n\nContext:\n{context}")
    ])
    
    context_str = "\n".join([r['payload']['text_content'] for r in state['context']])
    
    llm = get_llm()
    if llm is None:
        return {"context_quality_score": "good"}
        
    if llm == "gemini-native":
        # Bypass Gemini LLM call to save API rate limits
        print("Context Quality: good (bypassed LLM check)")
        return {"context_quality_score": "good"}
        
    chain = prompt | llm
    response = await chain.ainvoke({
        "question": state["original_question"],
        "context": context_str
    })
    
    score = "good" if "good" in str(response.content).strip().lower() else "poor"
    print(f"Context Quality: {score}")
    return {"context_quality_score": score}

async def generate_answer(state: AgentState) -> AgentState:
    """Generates the final conversational answer using the context."""
    print("--- GENERATING ANSWER ---")
    
    history_str = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in state.get('chat_history', [])])
    
    llm = get_llm()
    if llm is None:
        # Mock response for testing without a real API key
        print("Using mocked LLM response due to placeholder API key.")
        mock_response = TutorResponse(
            content="This is a mock response because the OpenAI API Key is not set.",
        )
        return {
            "answer": mock_response.model_dump(),
            "citations": []
        }

    if llm == "gemini-native":
        from google import genai
        import json
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        if not state.get("require_retrieval"):
            sys_prompt = """You are an expert personal study tutor. Adapt your teaching style precisely to the user's question.

For general educational questions, consider this response structure (but DO NOT force all sections if not needed):
1. Direct answer
2. Simple explanation
3. Detailed explanation
4. Example
5. Real-world analogy
6. Important points
7. Summary

ADAPT TO THE USER'S INTENT:
- If asked "What is X?", give a beginner-friendly explanation.
- If asked to "Explain in detail", give a detailed academic explanation.
- If asked for an "8-mark answer" or "exam answer", provide a highly structured, exam-oriented response.
- If asked "Explain like I'm a beginner", use very simple language.
- If asked for "only the definition", keep it extremely short.
- If asked to "Compare X and Y", always use a markdown table.
- If asked for code, provide properly formatted code blocks with explanations.
- For math questions, show the formula, explain variables, show calculation steps, and highlight the final answer.
- If using math formulas, use LaTeX markdown (e.g., $...$ or $$...$$).

Never unnecessarily repeat the entire previous conversation. Keep the flow natural."""
            user_prompt = f"Conversation History:\n{history_str}\n\nUser: {state['original_question']}"
            
            from google.genai import types
            import base64
            import re
            
            gemini_contents = []
            if state.get("image_data"):
                try:
                    match = re.match(r'data:(image/[a-zA-Z0-9]+);base64,(.*)', state['image_data'])
                    if match:
                        mime_type = match.group(1)
                        b64_data = match.group(2)
                        image_bytes = base64.b64decode(b64_data)
                        gemini_contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
                except Exception as e:
                    print(f"Failed to decode image: {e}")
                    
            gemini_contents.append(f"System: {sys_prompt}\n\nUser: {user_prompt}")
            
            print("[TUTOR] Gemini request started")
            print("[TUTOR] Number of Gemini calls: 1")
            
            response = await client.aio.models.generate_content_stream(
                model='gemini-3.5-flash',
                contents=gemini_contents,
            )
            
            stream_queue = state.get("stream_queue")
            full_text = ""
            async for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    if stream_queue:
                        await stream_queue.put(chunk.text)
            
            print("[TUTOR] Gemini request completed")
            
            answer_dict = {"content": full_text}
                
            return {
                "answer": answer_dict,
                "citations": []
            }
        else:
            sys_prompt = """You are an expert personal study tutor. Adapt your teaching style precisely to the user's question.

For general educational questions, consider this response structure (but DO NOT force all sections if not needed):
1. Direct answer
2. Simple explanation
3. Detailed explanation
4. Example
5. Real-world analogy
6. Important points
7. Summary

ADAPT TO THE USER'S INTENT:
- If asked "What is X?", give a beginner-friendly explanation.
- If asked to "Explain in detail", give a detailed academic explanation.
- If asked for an "8-mark answer" or "exam answer", provide a highly structured, exam-oriented response.
- If asked "Explain like I'm a beginner", use very simple language.
- If asked for "only the definition", keep it extremely short.
- If asked to "Compare X and Y", always use a markdown table.
- If asked for code, provide properly formatted code blocks with explanations.
- For math questions, show the formula, explain variables, show calculation steps, and highlight the final answer.
- If using math formulas, use LaTeX markdown (e.g., $...$ or $$...$$).

Never unnecessarily repeat the entire previous conversation. Keep the flow natural.

CRITICAL RULE: Answer the user's question directly based ONLY on the provided context. If the context does not contain the answer, say so clearly. Never hallucinate facts outside the context."""
            context_str = "\n\n".join([f"Source ({r['payload'].get('section_title', 'Unknown')}): {r['payload']['text_content']}" for r in state['context']])
            user_prompt = f"Conversation History:\n{history_str}\n\nQuestion: {state['original_question']}\n\nContext:\n{context_str}"
            
            from google.genai import types
            import base64
            import re
            
            gemini_contents = []
            if state.get("image_data"):
                try:
                    match = re.match(r'data:(image/[a-zA-Z0-9]+);base64,(.*)', state['image_data'])
                    if match:
                        mime_type = match.group(1)
                        b64_data = match.group(2)
                        image_bytes = base64.b64decode(b64_data)
                        gemini_contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
                except Exception as e:
                    print(f"Failed to decode image: {e}")
                    
            gemini_contents.append(f"System: {sys_prompt}\n\nUser: {user_prompt}")
            
            print("[TUTOR] Gemini request started")
            print("[TUTOR] Number of Gemini calls: 1")
            
            response = await client.aio.models.generate_content_stream(
                model='gemini-3.5-flash',
                contents=gemini_contents,
            )
            
            stream_queue = state.get("stream_queue")
            full_text = ""
            async for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    if stream_queue:
                        await stream_queue.put(chunk.text)
            
            print("[TUTOR] Gemini request completed")
                        
            from typing import Dict, Any
            answer_dict: Dict[str, Any] = {"content": full_text}
                
            doc_names = state.get("document_names", {})
            citations = []
            for r in state['context']:
                doc_id = str(r['payload'].get('document_id', ''))
                citations.append({
                    "document_name": doc_names.get(doc_id, "Unknown Document"),
                    "page_number": r['payload'].get('page_number'),
                    "section_title": r['payload'].get('section_title'),
                    "document_id": doc_id,
                    "relevance_score": round(r.get('score', 0.0), 2)
                })
            
            answer_dict["citations"] = citations
            
            return {
                "answer": answer_dict,
                "citations": citations
            }
            
    
    if not state.get("require_retrieval"):
        # General conversation fallback
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert personal study tutor. Adapt your teaching style precisely to the user's question.

For general educational questions, consider this response structure (but DO NOT force all sections if not needed):
1. Direct answer
2. Simple explanation
3. Detailed explanation
4. Example
5. Real-world analogy
6. Important points
7. Summary

ADAPT TO THE USER'S INTENT:
- If asked "What is X?", give a beginner-friendly explanation.
- If asked to "Explain in detail", give a detailed academic explanation.
- If asked for an "8-mark answer" or "exam answer", provide a highly structured, exam-oriented response.
- If asked "Explain like I'm a beginner", use very simple language.
- If asked for "only the definition", keep it extremely short.
- If asked to "Compare X and Y", always use a markdown table.
- If asked for code, provide properly formatted code blocks with explanations.
- For math questions, show the formula, explain variables, show calculation steps, and highlight the final answer.
- If using math formulas, use LaTeX markdown (e.g., $...$ or $$...$$).

Never unnecessarily repeat the entire previous conversation. Keep the flow natural."""),
            ("user", "Conversation History:\n{history}\n\nUser: {question}")
        ])
        chain = prompt | llm
        response = await chain.ainvoke({"question": state["original_question"], "history": history_str})
        
        answer_dict = {"content": response.content}
            
        return {
            "answer": answer_dict,
            "citations": []
        }
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert personal study tutor. Adapt your teaching style precisely to the user's question.

For general educational questions, consider this response structure (but DO NOT force all sections if not needed):
1. Direct answer
2. Simple explanation
3. Detailed explanation
4. Example
5. Real-world analogy
6. Important points
7. Summary

ADAPT TO THE USER'S INTENT:
- If asked "What is X?", give a beginner-friendly explanation.
- If asked to "Explain in detail", give a detailed academic explanation.
- If asked for an "8-mark answer" or "exam answer", provide a highly structured, exam-oriented response.
- If asked "Explain like I'm a beginner", use very simple language.
- If asked for "only the definition", keep it extremely short.
- If asked to "Compare X and Y", always use a markdown table.
- If asked for code, provide properly formatted code blocks with explanations.
- For math questions, show the formula, explain variables, show calculation steps, and highlight the final answer.
- If using math formulas, use LaTeX markdown (e.g., $...$ or $$...$$).

Never unnecessarily repeat the entire previous conversation. Keep the flow natural.

CRITICAL RULE: Answer the user's question directly based ONLY on the provided context. If the context does not contain the answer, say so clearly. Never hallucinate facts outside the context."""),
        ("user", "Conversation History:\n{history}\n\nQuestion: {question}\n\nContext:\n{context}")
    ])
    
    context_str = "\n\n".join([f"Source ({r['payload'].get('section_title', 'Unknown')}): {r['payload']['text_content']}" for r in state['context']])
    chain = prompt | llm
    
    response = await chain.ainvoke({
        "question": state["original_question"],
        "context": context_str,
        "history": history_str
    })
    
    # Attach precise citations from the state
    doc_names = state.get("document_names", {})
    citations = []
    for r in state['context']:
        doc_id = str(r['payload'].get('document_id', ''))
        citations.append({
            "document_name": doc_names.get(doc_id, "Unknown Document"),
            "page_number": r['payload'].get('page_number'),
            "section_title": r['payload'].get('section_title'),
            "document_id": doc_id,
            "relevance_score": round(r.get('score', 0.0), 2)
        })
    
    answer_dict = {"content": response.content}
    answer_dict["citations"] = citations
    
    return {
        "answer": answer_dict,
        "citations": citations
    }
