import os
import shutil
import urllib.parse
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Importing your logic from the other files
from pdf_extractor import extract_pdf_data
from structure_detector import transform_to_html
from epub_builder import build_epub

app = FastAPI(title="PDF to Reflowable EPUB Converter")

# 1. CORS Configuration
# This allows your React frontend (localhost:5173) to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cleanup_temp_files(file_paths: list):
    """
    Deletes temporary files. 
    This is called by BackgroundTasks ONLY after the FileResponse is finished.
    """
    for path in file_paths:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"Successfully deleted: {path}")
            except Exception as e:
                print(f"Error during cleanup of {path}: {e}")

@app.get("/")
def health_check():
    return {"status": "online", "message": "PDF-to-EPUB API is running"}

@app.post("/convert")
async def convert_pdf_to_epub(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Validate file extension
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # 1. Setup absolute paths to prevent "File Not Found" errors
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_filename = f"incoming_{file.filename}"
    output_filename = input_filename.replace(".pdf", ".epub")
    
    input_path = os.path.join(base_dir, input_filename)
    output_path = os.path.join(base_dir, output_filename)

    # 2. Save the uploaded stream to a physical file
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {str(e)}")

    try:
        # 3. THE CONVERSION PIPELINE
        # Step A: Extract raw text and metadata
        raw_data = extract_pdf_data(input_path)

        # Step B: Reconstruct paragraphs for reflowable logic
        html_content = transform_to_html(raw_data)

        # Step C: Package into a valid EPUB ZIP container
        build_epub(html_content, output_path, title=file.filename)

        # Verify the file was actually created and is not 0 bytes
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise Exception("EPUB generation resulted in an empty or missing file.")

        # 4. Schedule cleanup to run AFTER the download is complete
        background_tasks.add_task(cleanup_temp_files, [input_path, output_path])

        # 5. Prepare safe filename for headers (handles spaces/special characters)
        friendly_name = file.filename.replace(".pdf", ".epub")
        safe_filename = urllib.parse.quote(friendly_name)

        # 6. Return the file as a binary stream
        return FileResponse(
            path=output_path, 
            filename=friendly_name,
            media_type='application/epub+zip',
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}"
            }
        )

    except Exception as e:
        # Immediate cleanup if an error occurs before the response starts
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        
        print(f"PIPELINE ERROR: {str(e)}")
        # Return a proper HTTP 500 so clients receive an error status (not a saved .epub file)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")