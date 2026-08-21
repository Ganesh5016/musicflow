# MusicFlow

## Overview
MusicFlow is a full‑stack music player that lets you upload MP3 files, browse your library and stream songs directly from the browser.

## Features
- Upload MP3 files (title and artist metadata are optional)
- List all uploaded tracks
- Stream songs with HTML5 audio
- Simple management UI (delete tracks)

## Tech Stack
- **Frontend:** Vanilla HTML5, CSS3, JavaScript (Fetch API)
- **Backend:** Python 3.10+, FastAPI, Uvicorn
- **Database:** SQLite (via SQLAlchemy)

## Setup
1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd <repo-dir>
   ```
2. **Create a virtual environment & install deps**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Run the backend**
   ```bash
   uvicorn backend:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.
4. **Open the frontend**
   Open `frontend.html` in a web browser. No additional server is required for the static page.

## API Endpoints
- `GET /api/songs` – Returns a JSON list of songs.
- `GET /api/songs/{song_id}` – Streams the requested MP3 file.
- `POST /api/upload` – Upload a new MP3 (multipart/form-data). Fields: `title`, `artist`, `file`.
- `DELETE /api/songs/{song_id}` – Delete a song.

## License
MIT
