from fastapi import FastAPI, UploadFile
import asyncpg
from dotenv import load_dotenv
import os
import aiofiles

app = FastAPI()


load_dotenv()


connection_string = os.getenv("DATABASE_URL")
pool = None

@app.on_event("startup")
async def startup_event():
    global pool
    print("Creating connection pool")
    pool = await asyncpg.create_pool(connection_string)

@app.on_event("shutdown")
async def startup_event():
    global pool
    await pool.close()

@app.post("/images")
async def create_image():
    global pool
    image_name="SUII" 
    file_path="bin/bash"
    async with pool.acquire() as conn:
        # Execute SQL command to insert the image into the database
        await conn.execute('INSERT INTO image VALUES (default, $1, $2)', image_name, file_path)

    return {"message": "Image created successfully"}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    global pool
    save_directory = "uploaded_files"
    os.makedirs(save_directory, exist_ok=True)
    
    # Ensure the filename is safe to use
    safe_filename = file.filename.replace("..", "").replace("/", "").replace("\\", "")
    file_path = os.path.join(save_directory, safe_filename)
    
    # Use aiofiles for async file writing
    async with aiofiles.open(file_path, "wb") as buffer:
        while content := await file.read(1024):  
            await buffer.write(content)
    print(f"File saved to {file_path}")

    async with pool.acquire() as conn:
        # Execute SQL command to insert the image into the database
        await conn.execute('INSERT INTO image VALUES (default, $1, $2)', safe_filename, file_path)
   