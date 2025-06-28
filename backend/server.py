from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Song(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    artist: str
    album: str
    duration: int  # in seconds
    genre: str
    audio_url: str
    cover_art: str
    release_date: datetime = Field(default_factory=datetime.utcnow)

class SongCreate(BaseModel):
    title: str
    artist: str
    album: str
    duration: int
    genre: str
    audio_url: str
    cover_art: str

class Playlist(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    user_id: str
    song_ids: List[str] = []
    cover_art: str
    is_public: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PlaylistCreate(BaseModel):
    name: str
    description: str
    user_id: str
    cover_art: str = ""
    is_public: bool = True

class PlayHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    song_id: str
    played_at: datetime = Field(default_factory=datetime.utcnow)

# Initialize sample data
@api_router.on_event("startup")
async def init_sample_data():
    # Check if songs already exist
    existing_songs = await db.songs.count_documents({})
    if existing_songs == 0:
        sample_songs = [
            {
                "id": str(uuid.uuid4()),
                "title": "Electric Dreams",
                "artist": "Neon Pulse",
                "album": "Synthetic Nights",
                "duration": 213,
                "genre": "Electronic",
                "audio_url": "https://www.soundjay.com/misc/preview/bell-ringing-05.mp3",
                "cover_art": "https://images.pexels.com/photos/7676248/pexels-photo-7676248.jpeg",
                "release_date": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Midnight Jazz",
                "artist": "Soul Collective",
                "album": "Late Night Sessions",
                "duration": 267,
                "genre": "Jazz",
                "audio_url": "https://www.soundjay.com/misc/preview/bell-ringing-05.mp3",
                "cover_art": "https://images.pexels.com/photos/5475761/pexels-photo-5475761.jpeg",
                "release_date": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Purple Rain Dance",
                "artist": "Violet Storm",
                "album": "Color Symphony",
                "duration": 195,
                "genre": "Pop",
                "audio_url": "https://www.soundjay.com/misc/preview/bell-ringing-05.mp3",
                "cover_art": "https://images.pexels.com/photos/972377/pexels-photo-972377.jpeg",
                "release_date": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Guitar Serenity",
                "artist": "Acoustic Harmony",
                "album": "Strings of Peace",
                "duration": 245,
                "genre": "Acoustic",
                "audio_url": "https://www.soundjay.com/misc/preview/bell-ringing-05.mp3",
                "cover_art": "https://images.pexels.com/photos/8512209/pexels-photo-8512209.jpeg",
                "release_date": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Digital Beats",
                "artist": "Tech Sound",
                "album": "Binary Music",
                "duration": 188,
                "genre": "Electronic",
                "audio_url": "https://www.soundjay.com/misc/preview/bell-ringing-05.mp3",
                "cover_art": "https://images.unsplash.com/photo-1562876782-f324b8ac8e4c",
                "release_date": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Heartbeat Rhythm",
                "artist": "Love Frequency",
                "album": "Emotional Waves",
                "duration": 201,
                "genre": "Pop",
                "audio_url": "https://www.soundjay.com/misc/preview/bell-ringing-05.mp3",
                "cover_art": "https://images.unsplash.com/photo-1511208038467-1c62a6d37b39",
                "release_date": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Smoke & Mirrors",
                "artist": "Mystic Vibes",
                "album": "Ethereal Sounds",
                "duration": 234,
                "genre": "Ambient",
                "audio_url": "https://www.soundjay.com/misc/preview/bell-ringing-05.mp3",
                "cover_art": "https://images.unsplash.com/photo-1508898578281-774ac4893c0c",
                "release_date": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Headphone Dreams",
                "artist": "Audio Bliss",
                "album": "Sound Escape",
                "duration": 278,
                "genre": "Chillout",
                "audio_url": "https://www.soundjay.com/misc/preview/bell-ringing-05.mp3",
                "cover_art": "https://images.unsplash.com/photo-1567928513899-997d98489fbd",
                "release_date": datetime.utcnow()
            }
        ]
        await db.songs.insert_many(sample_songs)

# Auth endpoints
@api_router.post("/auth/register", response_model=User)
async def register(user: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_obj = User(username=user.username, email=user.email)
    await db.users.insert_one(user_obj.dict())
    return user_obj

@api_router.post("/auth/login", response_model=User)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return User(**user)

# Music endpoints
@api_router.get("/songs", response_model=List[Song])
async def get_songs():
    songs = await db.songs.find().to_list(1000)
    return [Song(**song) for song in songs]

@api_router.get("/songs/search")
async def search_songs(q: str):
    songs = await db.songs.find({
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"artist": {"$regex": q, "$options": "i"}},
            {"album": {"$regex": q, "$options": "i"}},
            {"genre": {"$regex": q, "$options": "i"}}
        ]
    }).to_list(100)
    return [Song(**song) for song in songs]

@api_router.get("/songs/{song_id}", response_model=Song)
async def get_song(song_id: str):
    song = await db.songs.find_one({"id": song_id})
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return Song(**song)

@api_router.post("/songs", response_model=Song)
async def create_song(song: SongCreate):
    song_obj = Song(**song.dict())
    await db.songs.insert_one(song_obj.dict())
    return song_obj

# Playlist endpoints
@api_router.get("/playlists", response_model=List[Playlist])
async def get_playlists(user_id: Optional[str] = None):
    query = {"user_id": user_id} if user_id else {"is_public": True}
    playlists = await db.playlists.find(query).to_list(100)
    return [Playlist(**playlist) for playlist in playlists]

@api_router.post("/playlists", response_model=Playlist)
async def create_playlist(playlist: PlaylistCreate):
    playlist_obj = Playlist(**playlist.dict())
    await db.playlists.insert_one(playlist_obj.dict())
    return playlist_obj

@api_router.get("/playlists/{playlist_id}", response_model=Playlist)
async def get_playlist(playlist_id: str):
    playlist = await db.playlists.find_one({"id": playlist_id})
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return Playlist(**playlist)

@api_router.put("/playlists/{playlist_id}/songs/{song_id}")
async def add_song_to_playlist(playlist_id: str, song_id: str):
    playlist = await db.playlists.find_one({"id": playlist_id})
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    if song_id not in playlist.get("song_ids", []):
        await db.playlists.update_one(
            {"id": playlist_id},
            {"$push": {"song_ids": song_id}}
        )
    return {"message": "Song added to playlist"}

@api_router.delete("/playlists/{playlist_id}/songs/{song_id}")
async def remove_song_from_playlist(playlist_id: str, song_id: str):
    await db.playlists.update_one(
        {"id": playlist_id},
        {"$pull": {"song_ids": song_id}}
    )
    return {"message": "Song removed from playlist"}

@api_router.get("/playlists/{playlist_id}/songs", response_model=List[Song])
async def get_playlist_songs(playlist_id: str):
    playlist = await db.playlists.find_one({"id": playlist_id})
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    song_ids = playlist.get("song_ids", [])
    songs = await db.songs.find({"id": {"$in": song_ids}}).to_list(1000)
    return [Song(**song) for song in songs]

# Play history
@api_router.post("/play-history")
async def record_play(user_id: str, song_id: str):
    play_record = PlayHistory(user_id=user_id, song_id=song_id)
    await db.play_history.insert_one(play_record.dict())
    return {"message": "Play recorded"}

@api_router.get("/play-history/{user_id}")
async def get_play_history(user_id: str):
    history = await db.play_history.find({"user_id": user_id}).sort("played_at", -1).limit(50).to_list(50)
    # Convert MongoDB documents to dictionaries to ensure JSON serialization
    return [
        {
            "id": item.get("id"),
            "user_id": item.get("user_id"),
            "song_id": item.get("song_id"),
            "played_at": item.get("played_at")
        } 
        for item in history
    ]

# Artists and Albums
@api_router.get("/artists")
async def get_artists():
    artists = await db.songs.distinct("artist")
    return [{"name": artist} for artist in artists]

@api_router.get("/albums")
async def get_albums():
    pipeline = [
        {"$group": {
            "_id": "$album",
            "artist": {"$first": "$artist"},
            "cover_art": {"$first": "$cover_art"},
            "song_count": {"$sum": 1}
        }}
    ]
    albums = await db.songs.aggregate(pipeline).to_list(100)
    return [{"name": album["_id"], "artist": album["artist"], "cover_art": album["cover_art"], "song_count": album["song_count"]} for album in albums]

@api_router.get("/genres")
async def get_genres():
    genres = await db.songs.distinct("genre")
    return [{"name": genre} for genre in genres]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()