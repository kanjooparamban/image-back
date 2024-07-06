from fastapi import FastAPI, UploadFile
import os
import aiofiles
from databases import Database

app = FastAPI()

# Configure your PostgreSQL database connection here
DATABASE_URL = "postgresql://image_owner:wVeIv0ujTJ5x@ep-autumn-fire-a1wvd4tl.ap-southeast-1.aws.neon.tech/image?sslmode=require"
database = Database(DATABASE_URL)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    save_directory = "uploaded_files"
    os.makedirs(save_directory, exist_ok=True)
    
    safe_filename = file.filename.replace("..", "").replace("/", "").replace("\\", "")
    file_path = os.path.join(save_directory, safe_filename)
    
    async with aiofiles.open(file_path, "wb") as buffer:
        while content := await file.read(1024):  
            await buffer.write(content)
    print(f"File saved to {file_path}")

    # Replace SQLite operations with PostgreSQL
    query = """
        CREATE TABLE IF NOT EXISTS image (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL
        );
    """
    await database.execute(query=query)

    query = """
        INSERT INTO image (filename, filepath) VALUES (:filename, :filepath)
    """
    values = {"filename": safe_filename, "filepath": file_path}
    await database.execute(query=query, values=values)

    return {"filename": safe_filename, "path": file_path}