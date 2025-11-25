from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
from pathlib import Path
import json
from datetime import datetime
from decoders import BarcodeDecoder, PDF417Decoder, ImageProcessor
from pdf_generator import PDFReportGenerator
import uuid

app = FastAPI()

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Session storage (in-memory for now)
session_data = {
    "barcode": None,
    "pdf417": None,
    "checkbook": None,
    "card_front": None,
    "card_back": None,
    "timestamps": {}
}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/session")
async def get_session():
    """Get current session data"""
    return session_data

@app.post("/reset")
async def reset_session():
    """Reset all session data and clear uploads"""
    global session_data
    
    # Clear upload directory and ensure it exists afterwards
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    UPLOAD_DIR.mkdir(exist_ok=True)
    
    # Reset session data
    session_data = {
        "barcode": None,
        "pdf417": None,
        "checkbook": None,
        "card_front": None,
        "card_back": None,
        "timestamps": {}
    }
    
    return {"message": "Session reset successfully"}

@app.post("/upload/barcode")
async def upload_barcode(file: UploadFile = File(...)):
    """Upload and decode barcode image"""
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"barcode_{file_id}.png"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Decode barcode
        result = BarcodeDecoder.decode_barcode(file_path)
        
        if "error" in result:
            return JSONResponse(status_code=400, content=result)
        
        # Store in session
        session_data["barcode"] = {
            **result,
            "path": str(file_path),
            "filename": file.filename
        }
        session_data["timestamps"]["barcode"] = datetime.now().isoformat()
        
        return {"success": True, "data": session_data["barcode"]}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/upload/pdf417")
async def upload_pdf417(file: UploadFile = File(...)):
    """Upload and decode PDF417 image"""
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"pdf417_{file_id}.png"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Decode PDF417
        result = PDF417Decoder.decode_pdf417(file_path)
        
        if "error" in result:
            return JSONResponse(status_code=400, content=result)
        
        # Store in session
        session_data["pdf417"] = {
            **result,
            "path": str(file_path),
            "filename": file.filename
        }
        session_data["timestamps"]["pdf417"] = datetime.now().isoformat()
        
        return {"success": True, "data": session_data["pdf417"]}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/upload/checkbook")
async def upload_checkbook(file: UploadFile = File(...)):
    """Upload checkbook scan"""
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"checkbook_{file_id}.png"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process image
        result = ImageProcessor.process_image(file_path, "checkbook")
        
        if "error" in result:
            return JSONResponse(status_code=400, content=result)
        
        # Store in session
        session_data["checkbook"] = {
            **result.get("image_info", {}),
            "path": str(file_path),
            "filename": file.filename
        }
        session_data["timestamps"]["checkbook"] = datetime.now().isoformat()
        
        return {"success": True, "data": session_data["checkbook"]}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/upload/card")
async def upload_card(front: UploadFile = File(None), back: UploadFile = File(None)):
    """Upload card front and/or back"""
    try:
        results = {}
        
        # Process front
        if front:
            file_id = str(uuid.uuid4())
            file_path = UPLOAD_DIR / f"card_front_{file_id}.png"
            
            with open(file_path, "wb") as f:
                content = await front.read()
                f.write(content)
            
            result = ImageProcessor.process_image(file_path, "card_front")
            
            if "error" not in result:
                session_data["card_front"] = {
                    **result.get("image_info", {}),
                    "path": str(file_path),
                    "filename": front.filename
                }
                session_data["timestamps"]["card_front"] = datetime.now().isoformat()
                results["front"] = session_data["card_front"]
        
        # Process back
        if back:
            file_id = str(uuid.uuid4())
            file_path = UPLOAD_DIR / f"card_back_{file_id}.png"
            
            with open(file_path, "wb") as f:
                content = await back.read()
                f.write(content)
            
            result = ImageProcessor.process_image(file_path, "card_back")
            
            if "error" not in result:
                session_data["card_back"] = {
                    **result.get("image_info", {}),
                    "path": str(file_path),
                    "filename": back.filename
                }
                session_data["timestamps"]["card_back"] = datetime.now().isoformat()
                results["back"] = session_data["card_back"]
        
        if not results:
            return JSONResponse(status_code=400, content={"error": "No files provided"})
        
        return {"success": True, "data": results}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/generate-pdf")
async def generate_pdf():
    """Generate and download combined PDF report"""
    try:
        filename = "scan_report.pdf"
        
        if session_data.get("pdf417"):
            pdf417_data = session_data["pdf417"]
            for data in pdf417_data.get("pdf417_data", []):
                if data.get("parsed") and data["parsed"].get("user"):
                    user = data["parsed"]["user"]
                    # Use original casing from PDF417, trim outer spaces and
                    # replace inner spaces with underscores so the filename is
                    # Firstname_Lastname.pdf.
                    first_name = user.get("first", "").strip().replace(" ", "_")
                    last_name = user.get("last", "").strip().replace(" ", "_")
                    
                    if first_name and last_name:
                        filename = f"{first_name}_{last_name}.pdf"
                        break
        
        output_path = UPLOAD_DIR / filename
        generator = PDFReportGenerator(str(output_path))
        result = generator.generate_report(session_data)
        
        if "error" in result:
            return JSONResponse(status_code=500, content=result)
        
        return FileResponse(
            path=output_path,
            filename=filename,
            media_type="application/pdf"
        )
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/generate-pdf-selective")
async def generate_pdf_selective(selected_items: dict):
    """Generate PDF with only selected scan types"""
    try:
        # Filter session data based on selected items
        filtered_data = {
            "barcode": session_data["barcode"] if selected_items.get("barcode") else None,
            "pdf417": session_data["pdf417"] if selected_items.get("pdf417") else None,
            "checkbook": session_data["checkbook"] if selected_items.get("checkbook") else None,
            "card_front": session_data["card_front"] if selected_items.get("card_front") else None,
            "card_back": session_data["card_back"] if selected_items.get("card_back") else None,
            "timestamps": session_data["timestamps"]
        }
        
        filename = "scan_report.pdf"
        
        if filtered_data.get("pdf417"):
            pdf417_data = filtered_data["pdf417"]
            for data in pdf417_data.get("pdf417_data", []):
                if data.get("parsed") and data["parsed"].get("user"):
                    user = data["parsed"]["user"]
                    # Same filename logic for selective export
                    first_name = user.get("first", "").strip().replace(" ", "_")
                    last_name = user.get("last", "").strip().replace(" ", "_")
                    
                    if first_name and last_name:
                        filename = f"{first_name}_{last_name}.pdf"
                        break
        
        output_path = UPLOAD_DIR / filename
        generator = PDFReportGenerator(str(output_path))
        result = generator.generate_report(filtered_data)
        
        if "error" in result:
            return JSONResponse(status_code=500, content=result)
        
        return FileResponse(
            path=output_path,
            filename=filename,
            media_type="application/pdf"
        )
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
