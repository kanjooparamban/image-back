from fastapi import FastAPI, UploadFile
import os
import sqlite3
import aiofiles

app = FastAPI()

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
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

    try:
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image (
                id INTEGER PRIMARY KEY,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            INSERT INTO image (filename, filepath) VALUES (?, ?)
        ''', (safe_filename, file_path))
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return {"error": "Database operation failed"}
    finally:
        conn.close()
    
    return {"filename": safe_filename, "path": file_path}