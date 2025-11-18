import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportRequest(BaseModel):
    title: str = Field(default="Seminar Report: The Web (World Wide Web)")
    pages: int = Field(default=80, ge=1, le=200)
    section_title: str = Field(default="Chapter: The Evolution of the Web")
    section_body: str = Field(default=(
        "The Web has evolved from a collection of static documents into a dynamic, interactive, and intelligent ecosystem.\n"
        "It started with Web 1.0, primarily focused on static pages, progressed into Web 2.0 characterized by user-generated content "
        "and social platforms, and is currently transitioning into Web 3.0, which emphasizes decentralization, security, trustless systems, "
        "semantic understanding, and immersive digital experiences.\n\n"
        "The Web continues to be the backbone of the digital era, enabling communication, business, entertainment, and global connectivity.\n"
        "Detailed studies show that the future Web will integrate AI, blockchain, edge computing, and mixed reality technologies."
    ))
    filename: Optional[str] = Field(default="Web_Seminar_Report_80Pages.pdf")


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


@app.post("/generate-report")
def generate_report(payload: ReportRequest):
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.enums import TA_JUSTIFY
        from reportlab.lib.styles import ParagraphStyle

        styles = getSampleStyleSheet()
        base_style = styles["Normal"]
        base_style.leading = 16
        body_style = ParagraphStyle(name="Body", parent=base_style, alignment=TA_JUSTIFY)
        title_style = styles["Title"]

        content = []

        intro_text = f"""
        <b>{payload.title}</b><br/><br/>
        This report provides an extensive analysis of the Web, its evolution, architecture, technologies, applications, and future trends.
        """
        content.append(Paragraph(intro_text, title_style))
        content.append(PageBreak())

        section_html = f"""
        <b>{payload.section_title}</b><br/><br/>
        {payload.section_body.replace('\n', '<br/>')}
        """
        # We already used 2 entries (intro + PageBreak), now repeat for pages-1 times
        pages_to_add = max(payload.pages - 1, 1)
        for _ in range(pages_to_add):
            content.append(Paragraph(section_html, body_style))
            content.append(PageBreak())

        safe_name = payload.filename or "Web_Seminar_Report_80Pages.pdf"
        if not safe_name.lower().endswith(".pdf"):
            safe_name += ".pdf"
        out_dir = "/mnt/data"
        os.makedirs(out_dir, exist_ok=True)
        file_path = os.path.join(out_dir, safe_name)

        doc = SimpleDocTemplate(file_path, pagesize=A4)
        doc.build(content)
        return {"status": "ok", "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
