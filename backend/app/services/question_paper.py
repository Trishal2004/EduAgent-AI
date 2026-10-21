import os
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from uuid import UUID
from fpdf import FPDF
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.models.document import Document
from app.models.processed_chunk import ProcessedChunk
from app.repositories.question_paper import QuestionPaperRepository
from app.DTOs.question_paper import QuestionPaperGeneration, PaperPatternEnum
from app.config.config import settings

class PDFGenerator(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 15)
        self.cell(0, 10, "University Examination", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

class QuestionPaperService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.paper_repo = QuestionPaperRepository(db)
        self.llm = ChatOpenAI(temperature=0.3, api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini")

    async def generate_paper(self, document_id: UUID, owner_id: UUID, pattern: PaperPatternEnum):
        # 1. Verify document
        doc_result = await self.db.execute(select(Document).where(Document.id == document_id, Document.owner_id == owner_id))
        doc = doc_result.scalars().first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # 2. Gather Document Context
        chunk_result = await self.db.execute(
            select(ProcessedChunk)
            .where(ProcessedChunk.document_id == document_id)
            .order_by(ProcessedChunk.page_number, ProcessedChunk.chunk_index)
        )
        chunks = chunk_result.scalars().all()
        if not chunks:
            raise HTTPException(status_code=400, detail="No text chunks found for this document")

        full_text = "\n\n".join([chunk.text_content for chunk in chunks])

        # 3. Generate Structured Paper using LLM
        structured_llm = self.llm.with_structured_output(QuestionPaperGeneration)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert university examiner. Generate a formal question paper based on the provided text. "
                       f"The pattern is {pattern.value}. "
                       "You MUST generate 3 distinct sections: Part A (2 Marks questions), Part B (5 Marks questions), and Part C (10 Marks questions). "
                       "Provide clear instructions for each section. "
                       "For EACH question, you MUST provide a detailed 'model_answer' containing the key points expected from the student."),
            ("user", "Document Text:\n{context}")
        ])
        
        chain = prompt | structured_llm
        response: QuestionPaperGeneration = await chain.ainvoke({"context": full_text})
        
        # 4. Generate PDF
        pdf_path = self._generate_pdf(response, document_id)

        # 5. Save to Database
        saved_paper = await self.paper_repo.create(
            document_id=document_id,
            owner_id=owner_id,
            paper_type=pattern.value,
            content_json=response.dict(),
            pdf_file_path=pdf_path
        )
        
        return saved_paper

    def _generate_pdf(self, paper: QuestionPaperGeneration, document_id: UUID) -> str:
        pdf = PDFGenerator()
        pdf.add_page()
        
        # Title
        pdf.set_font("helvetica", "B", 16)
        pdf.multi_cell(0, 10, paper.title, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)
        
        for section in paper.sections:
            # Section Header
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, section.section_name, new_x="LMARGIN", new_y="NEXT")
            
            # Instructions
            pdf.set_font("helvetica", "I", 12)
            pdf.multi_cell(0, 8, section.instructions, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            
            # Questions
            pdf.set_font("helvetica", "", 12)
            for idx, q in enumerate(section.questions, 1):
                # We use encode/decode to prevent latin-1 character errors in FPDF
                safe_q = q.question.encode('latin-1', 'replace').decode('latin-1')
                question_text = f"{idx}. {safe_q}"
                
                # Align text left, marks right (roughly)
                pdf.cell(170, 8, question_text)
                pdf.cell(20, 8, f"[{q.marks}]", align="R", new_x="LMARGIN", new_y="NEXT")
                
            pdf.ln(10)
            
        # Append Answer Key
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.multi_cell(0, 10, "ANSWER KEY & MODEL ANSWERS", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)
        
        for section in paper.sections:
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, section.section_name, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            for idx, q in enumerate(section.questions, 1):
                safe_q = q.question.encode('latin-1', 'replace').decode('latin-1')
                safe_ans = q.model_answer.encode('latin-1', 'replace').decode('latin-1')
                
                pdf.set_font("helvetica", "B", 12)
                pdf.multi_cell(0, 8, f"Q{idx}. {safe_q} [{q.marks} Marks]", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", "", 12)
                pdf.multi_cell(0, 6, f"Answer:\n{safe_ans}", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(5)
            
        # Save file
        upload_dir = "uploads/papers"
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{upload_dir}/{uuid.uuid4()}.pdf"
        
        pdf.output(filename)
        return filename
