#!/usr/bin/env python3
import requests
import json
import uuid
import time
from pprint import pprint

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://26768b7b-0aec-477e-9f51-1026593687bb.preview.emergentagent.com/api"

# Test results tracking
test_results = {
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "failures": []
}

def run_test(test_name, test_func):
    """Run a test and track results"""
    print(f"\n{'='*80}\nTesting: {test_name}\n{'='*80}")
    test_results["total_tests"] += 1
    
    try:
        result = test_func()
        if result:
            test_results["passed_tests"] += 1
            print(f"✅ PASSED: {test_name}")
            return True
        else:
            test_results["failed_tests"] += 1
            test_results["failures"].append(test_name)
            print(f"❌ FAILED: {test_name}")
            return False
    except Exception as e:
        test_results["failed_tests"] += 1
        test_results["failures"].append(f"{test_name}: {str(e)}")
        print(f"❌ FAILED: {test_name} - Exception: {str(e)}")
        return False

def test_get_songs():
    """Test GET /api/songs endpoint"""
    response = requests.get(f"{BACKEND_URL}/songs")
    
    # Check status code
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        return False
    
    # Check response data
    data = response.json()
    if not isinstance(data, list):
        print(f"Error: Expected list response, got {type(data)}")
        return False
    
    # Check if we have 8 sample songs
    if len(data) != 8:
        print(f"Error: Expected 8 sample songs, got {len(data)}")
        return False
    
    # Check song structure
    sample_song = data[0]
    required_fields = ["id", "title", "artist", "album", "duration", "genre", "audio_url", "cover_art"]
    for field in required_fields:
        if field not in sample_song:
            print(f"Error: Missing required field '{field}' in song data")
            return False
    
    print(f"Found {len(data)} songs with proper structure")
    return True

def test_search_songs():
    """Test GET /api/songs/search endpoint"""
    # Test search for "electric" which should match "Electric Dreams"
    response = requests.get(f"{BACKEND_URL}/songs/search?q=electric")
    
    # Check status code
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        return False
    
    # Check response data
    data = response.json()
    if not isinstance(data, list):
        print(f"Error: Expected list response, got {type(data)}")
        return False
    
    # Check if we found at least one song with "electric" in it
    if len(data) < 1:
        print(f"Error: Expected at least one song with 'electric', got {len(data)}")
        return False
    
    # Check if the first song has "Electric" in the title
    found_electric = False
    for song in data:
        if "Electric" in song["title"]:
            found_electric = True
            break
    
    if not found_electric:
        print(f"Error: Expected to find song with 'Electric' in title")
        return False
    
    print(f"Search found {len(data)} songs matching 'electric'")
    return True

def test_get_artists():
    """Test GET /api/artists endpoint"""
    response = requests.get(f"{BACKEND_URL}/artists")
    
    # Check status code
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        return False
    
    # Check response data
    data = response.json()
    if not isinstance(data, list):
        print(f"Error: Expected list response, got {type(data)}")
        return False
    
    # We should have at least 8 artists (one for each song)
    if len(data) < 1:
        print(f"Error: Expected at least one artist, got {len(data)}")
        return False
    
    # Check artist structure
    sample_artist = data[0]
    if "name" not in sample_artist:
        print(f"Error: Missing required field 'name' in artist data")
        return False
    
    print(f"Found {len(data)} artists with proper structure")
    return True

def test_get_albums():
    """Test GET /api/albums endpoint"""
    response = requests.get(f"{BACKEND_URL}/albums")
    
    # Check status code
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        return False
    
    # Check response data
    data = response.json()
    if not isinstance(data, list):
        print(f"Error: Expected list response, got {type(data)}")
        return False
    
    # We should have at least one album
    if len(data) < 1:
        print(f"Error: Expected at least one album, got {len(data)}")
        return False
    
    # Check album structure
    sample_album = data[0]
    required_fields = ["name", "artist", "cover_art", "song_count"]
    for field in required_fields:
        if field not in sample_album:
            print(f"Error: Missing required field '{field}' in album data")
            return False
    
    print(f"Found {len(data)} albums with proper structure")
    return True

def test_get_genres():
    """Test GET /api/genres endpoint"""
    response = requests.get(f"{BACKEND_URL}/genres")
    
    # Check status code
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        return False
    
    # Check response data
    data = response.json()
    if not isinstance(data, list):
        print(f"Error: Expected list response, got {type(data)}")
        return False
    
    # We should have at least one genre
    if len(data) < 1:
        print(f"Error: Expected at least one genre, got {len(data)}")
        return False
    
    # Check genre structure
    sample_genre = data[0]
    if "name" not in sample_genre:
        print(f"Error: Missing required field 'name' in genre data")
        return False
    
    print(f"Found {len(data)} genres with proper structure")
    return True

def test_user_registration():
    """Test POST /api/auth/register endpoint"""
    # Generate unique username and email
    unique_id = str(uuid.uuid4())[:8]
    test_user = {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=test_user)
    
    # Check status code
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    # Check response data
    data = response.json()
    if not isinstance(data, dict):
        print(f"Error: Expected dict response, got {type(data)}")
        return False
    
    # Check user structure
    required_fields = ["id", "username", "email", "created_at"]
    for field in required_fields:
        if field not in data:
            print(f"Error: Missing required field '{field}' in user data")
            return False
    
    # Verify the username and email match what we sent
    if data["username"] != test_user["username"]:
        print(f"Error: Username mismatch. Expected {test_user['username']}, got {data['username']}")
        return False
    
    if data["email"] != test_user["email"]:
        print(f"Error: Email mismatch. Expected {test_user['email']}, got {data['email']}")
        return False
    
    print(f"Successfully registered user: {data['username']}")
    
    # Store user for login test
    global registered_user
    registered_user = test_user
    return True

def test_user_login():
    """Test POST /api/auth/login endpoint"""
    # Use the user created in the registration test
    global registered_user
    
    if not registered_user:
        print("Error: No registered user available for login test")
        return False
    
    login_data = {
        "email": registered_user["email"],
        "password": registered_user["password"]
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    # Check status code
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    # Check response data
    data = response.json()
    if not isinstance(data, dict):
        print(f"Error: Expected dict response, got {type(data)}")
        return False
    
    # Check user structure
    required_fields = ["id", "username", "email", "created_at"]
    for field in required_fields:
        if field not in data:
            print(f"Error: Missing required field '{field}' in user data")
            return False
    
    # Verify the email matches what we sent
    if data["email"] != login_data["email"]:
        print(f"Error: Email mismatch. Expected {login_data['email']}, got {data['email']}")
        return False
    
    print(f"Successfully logged in user: {data['username']}")
    
    # Store user ID for other tests
    global user_id
    user_id = data["id"]
    return True

def test_create_playlist():
    """Test POST /api/playlists endpoint"""
    global user_id
    
    if not user_id:
        print("Error: No user ID available for playlist test")
        return False
    
    playlist_data = {
        "name": f"Test Playlist {str(uuid.uuid4())[:8]}",
        "description": "A test playlist created by the API test",
        "user_id": user_id,
        "cover_art": "https://images.pexels.com/photos/1021876/pexels-photo-1021876.jpeg",
        "is_public": True
    }
    
    response = requests.post(f"{BACKEND_URL}/playlists", json=playlist_data)
    
    # Check status code
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    # Check response data
    data = response.json()
    if not isinstance(data, dict):
        print(f"Error: Expected dict response, got {type(data)}")
        return False
    
    # Check playlist structure
    required_fields = ["id", "name", "description", "user_id", "song_ids", "cover_art", "is_public", "created_at"]
    for field in required_fields:
        if field not in data:
            print(f"Error: Missing required field '{field}' in playlist data")
            return False
    
    # Verify the name and user_id match what we sent
    if data["name"] != playlist_data["name"]:
        print(f"Error: Name mismatch. Expected {playlist_data['name']}, got {data['name']}")
        return False
    
    if data["user_id"] != playlist_data["user_id"]:
        print(f"Error: User ID mismatch. Expected {playlist_data['user_id']}, got {data['user_id']}")
        return False
    
    print(f"Successfully created playlist: {data['name']} with ID: {data['id']}")
    
    # Store playlist ID for other tests
    global playlist_id
    playlist_id = data["id"]
    return True

def test_get_playlists():
    """Test GET /api/playlists endpoint"""
    global user_id
    
    if not user_id:
        print("Error: No user ID available for get playlists test")
        return False
    
    # Get playlists for the test user
    response = requests.get(f"{BACKEND_URL}/playlists?user_id={user_id}")
    
    # Check status code
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        return False
    
    # Check response data
    data = response.json()
    if not isinstance(data, list):
        print(f"Error: Expected list response, got {type(data)}")
        return False
    
    # We should have at least one playlist (the one we created)
    if len(data) < 1:
        print(f"Error: Expected at least one playlist, got {len(data)}")
        return False
    
    # Check playlist structure
    sample_playlist = data[0]
    required_fields = ["id", "name", "description", "user_id", "song_ids", "cover_art", "is_public", "created_at"]
    for field in required_fields:
        if field not in sample_playlist:
            print(f"Error: Missing required field '{field}' in playlist data")
            return False
    
    print(f"Found {len(data)} playlists for user {user_id}")
    return True

def test_add_song_to_playlist():
    """Test PUT /api/playlists/{playlist_id}/songs/{song_id} endpoint"""
    global playlist_id
    
    if not playlist_id:
        print("Error: No playlist ID available for add song test")
        return False
    
    # First, get a song ID from the songs endpoint
    response = requests.get(f"{BACKEND_URL}/songs")
    if response.status_code != 200:
        print(f"Error: Failed to get songs for add to playlist test")
        return False
    
    songs = response.json()
    if not songs or len(songs) == 0:
        print(f"Error: No songs available for add to playlist test")
        return False
    
    song_id = songs[0]["id"]
    
    # Add the song to the playlist
    response = requests.put(f"{BACKEND_URL}/playlists/{playlist_id}/songs/{song_id}")
    
    # Check status code
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    # Check response data
    data = response.json()
    if not isinstance(data, dict):
        print(f"Error: Expected dict response, got {type(data)}")
        return False
    
    if "message" not in data:
        print(f"Error: Missing 'message' field in response")
        return False
    
    print(f"Successfully added song {song_id} to playlist {playlist_id}")
    
    # Store song ID for other tests
    global added_song_id
    added_song_id = song_id
    return True

def test_get_playlist_songs():
    """Test GET /api/playlists/{playlist_id}/songs endpoint"""
    global playlist_id, added_song_id
    
    if not playlist_id:
        print("Error: No playlist ID available for get playlist songs test")
        return False
    
    if not added_song_id:
        print("Error: No added song ID available for get playlist songs test")
        return False
    
    # Get songs in the playlist
    response = requests.get(f"{BACKEND_URL}/playlists/{playlist_id}/songs")
    
    # Check status code
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    # Check response data
    data = response.json()
    if not isinstance(data, list):
        print(f"Error: Expected list response, got {type(data)}")
        return False
    
    # We should have at least one song (the one we added)
    if len(data) < 1:
        print(f"Error: Expected at least one song in playlist, got {len(data)}")
        return False
    
    # Check if the added song is in the playlist
    found_song = False
    for song in data:
        if song["id"] == added_song_id:
            found_song = True
            break
    
    if not found_song:
        print(f"Error: Added song {added_song_id} not found in playlist songs")
        return False
    
    print(f"Found {len(data)} songs in playlist {playlist_id}, including our added song")
    return True

def test_record_play_history():
    """Test POST /api/play-history endpoint"""
    global user_id, added_song_id
    
    if not user_id:
        print("Error: No user ID available for play history test")
        return False
    
    if not added_song_id:
        print("Error: No song ID available for play history test")
        return False
    
    # Record a play
    response = requests.post(f"{BACKEND_URL}/play-history?user_id={user_id}&song_id={added_song_id}")
    
    # Check status code
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    # Check response data
    data = response.json()
    if not isinstance(data, dict):
        print(f"Error: Expected dict response, got {type(data)}")
        return False
    
    if "message" not in data:
        print(f"Error: Missing 'message' field in response")
        return False
    
    print(f"Successfully recorded play for user {user_id} and song {added_song_id}")
    return True

def test_get_play_history():
    """Test GET /api/play-history/{user_id} endpoint"""
    global user_id
    
    if not user_id:
        print("Error: No user ID available for get play history test")
        return False
    
    # Get play history
    response = requests.get(f"{BACKEND_URL}/play-history/{user_id}")
    
    # Check status code
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    # Check response data
    data = response.json()
    if not isinstance(data, list):
        print(f"Error: Expected list response, got {type(data)}")
        return False
    
    # We should have at least one play history entry (the one we just recorded)
    if len(data) < 1:
        print(f"Error: Expected at least one play history entry, got {len(data)}")
        return False
    
    print(f"Found {len(data)} play history entries for user {user_id}")
    return True

if __name__ == "__main__":
    print(f"\n{'='*80}\nTesting Music Streaming Backend API\n{'='*80}")
    print(f"Backend URL: {BACKEND_URL}")
    
    # Initialize global variables
    registered_user = None
    user_id = None
    playlist_id = None
    added_song_id = None
    
    # Run tests
    # 1. Music Library APIs
    run_test("Get Songs", test_get_songs)
    run_test("Search Songs", test_search_songs)
    run_test("Get Artists", test_get_artists)
    run_test("Get Albums", test_get_albums)
    run_test("Get Genres", test_get_genres)
    
    # 2. User Authentication
    run_test("User Registration", test_user_registration)
    run_test("User Login", test_user_login)
    
    # 3. Playlist Management
    run_test("Create Playlist", test_create_playlist)
    run_test("Get Playlists", test_get_playlists)
    run_test("Add Song to Playlist", test_add_song_to_playlist)
    run_test("Get Playlist Songs", test_get_playlist_songs)
    
    # 4. Play History
    run_test("Record Play History", test_record_play_history)
    run_test("Get Play History", test_get_play_history)
    
    # Print summary
    print(f"\n{'='*80}\nTest Summary\n{'='*80}")
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"Passed Tests: {test_results['passed_tests']}")
    print(f"Failed Tests: {test_results['failed_tests']}")
    
    if test_results['failed_tests'] > 0:
        print("\nFailed Tests:")
        for failure in test_results['failures']:
            print(f"- {failure}")
    
    if test_results['failed_tests'] == 0:
        print("\n✅ All tests passed! The backend API is working correctly.")
    else:
        print(f"\n❌ {test_results['failed_tests']} tests failed. Please check the issues above.")