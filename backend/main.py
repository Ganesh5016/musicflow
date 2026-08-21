import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'music.db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=True)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class SongOut(BaseModel):
    id: int
    title: str
    artist: str | None = None
    uploaded_at: datetime

    class Config:
        orm_mode = True

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/songs", response_model=list[SongOut])
async def list_songs():
    with SessionLocal() as db:
        songs = db.query(Song).order_by(Song.uploaded_at.desc()).all()
        return songs

@app.get("/api/songs/{song_id}")
async def stream_song(song_id: int):
    with SessionLocal() as db:
        song = db.query(Song).filter(Song.id == song_id).first()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        file_path = os.path.join(UPLOAD_DIR, song.filename)
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="File missing")
        return FileResponse(path=file_path, media_type='audio/mpeg', filename=song.filename)

@app.post("/api/upload")
async def upload_song(
    title: str = Form(...),
    artist: str = Form(None),
    file: UploadFile = File(...)
):
    if file.content_type != "audio/mpeg":
        raise HTTPException(status_code=400, detail="Only MP3 files are supported")
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    ext = os.path.splitext(file.filename)[1]
    safe_name = f"{timestamp}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(file_path, "wb") as out_file:
        content = await file.read()
        out_file.write(content)
    with SessionLocal() as db:
        new_song = Song(title=title or "Untitled", artist=artist, filename=safe_name)
        db.add(new_song)
        db.commit()
        db.refresh(new_song)
        return {"id": new_song.id, "message": "Uploaded successfully"}

@app.delete("/api/songs/{song_id}")
async def delete_song(song_id: int):
    with SessionLocal() as db:
        song = db.query(Song).filter(Song.id == song_id).first()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        file_path = os.path.join(UPLOAD_DIR, song.filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        db.delete(song)
        db.commit()
        return {"message": "Deleted successfully"}

# To run: uvicorn backend:app --reload
