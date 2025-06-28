import React, { useState, useEffect, useRef, createContext, useContext } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Context for managing global state
const MusicContext = createContext();

const MusicProvider = ({ children }) => {
  const [currentSong, setCurrentSong] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playlist, setPlaylist] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [user, setUser] = useState(null);
  const [shuffle, setShuffle] = useState(false);
  const [repeat, setRepeat] = useState('none'); // 'none', 'one', 'all'
  const audioRef = useRef(new Audio());

  const value = {
    currentSong, setCurrentSong,
    isPlaying, setIsPlaying,
    playlist, setPlaylist,
    currentIndex, setCurrentIndex,
    volume, setVolume,
    currentTime, setCurrentTime,
    duration, setDuration,
    user, setUser,
    shuffle, setShuffle,
    repeat, setRepeat,
    audioRef
  };

  return (
    <MusicContext.Provider value={value}>
      {children}
    </MusicContext.Provider>
  );
};

const useMusicContext = () => {
  const context = useContext(MusicContext);
  if (!context) {
    throw new Error('useMusicContext must be used within a MusicProvider');
  }
  return context;
};

// Components
const Sidebar = () => {
  const [activeSection, setActiveSection] = useState('home');
  const { user } = useMusicContext();

  const menuItems = [
    { id: 'home', icon: '🏠', label: 'Home' },
    { id: 'search', icon: '🔍', label: 'Search' },
    { id: 'library', icon: '📚', label: 'Your Library' },
    { id: 'playlists', icon: '🎵', label: 'Playlists' },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1 className="logo">🎵 StreamifyMusic</h1>
      </div>
      
      <nav className="sidebar-nav">
        {menuItems.map(item => (
          <button
            key={item.id}
            className={`nav-item ${activeSection === item.id ? 'active' : ''}`}
            onClick={() => setActiveSection(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>

      {user && (
        <div className="user-section">
          <div className="user-info">
            <div className="user-avatar">👤</div>
            <div className="user-details">
              <p className="user-name">{user.username}</p>
              <p className="user-email">{user.email}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const Player = () => {
  const {
    currentSong, isPlaying, setIsPlaying, currentTime, setCurrentTime,
    duration, setDuration, volume, setVolume, shuffle, setShuffle,
    repeat, setRepeat, playlist, currentIndex, setCurrentIndex, audioRef
  } = useMusicContext();

  useEffect(() => {
    const audio = audioRef.current;
    
    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    
    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', handleNext);
    
    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', handleNext);
    };
  }, []);

  useEffect(() => {
    if (currentSong) {
      audioRef.current.src = currentSong.audio_url;
      audioRef.current.load();
    }
  }, [currentSong]);

  useEffect(() => {
    audioRef.current.volume = volume;
  }, [volume]);

  const togglePlayPause = () => {
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handlePrevious = () => {
    if (playlist.length > 0) {
      const newIndex = currentIndex > 0 ? currentIndex - 1 : playlist.length - 1;
      setCurrentIndex(newIndex);
    }
  };

  const handleNext = () => {
    if (playlist.length > 0) {
      if (repeat === 'one') {
        audioRef.current.currentTime = 0;
        audioRef.current.play();
        return;
      }
      
      let newIndex;
      if (shuffle) {
        newIndex = Math.floor(Math.random() * playlist.length);
      } else {
        newIndex = currentIndex < playlist.length - 1 ? currentIndex + 1 : 0;
      }
      
      if (repeat === 'none' && newIndex === 0 && currentIndex === playlist.length - 1) {
        setIsPlaying(false);
        return;
      }
      
      setCurrentIndex(newIndex);
    }
  };

  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    const newTime = percent * duration;
    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  if (!currentSong) return null;

  return (
    <div className="player">
      <div className="player-song-info">
        <img src={currentSong.cover_art} alt={currentSong.title} className="player-cover" />
        <div className="player-text">
          <h4 className="player-title">{currentSong.title}</h4>
          <p className="player-artist">{currentSong.artist}</p>
        </div>
      </div>

      <div className="player-controls">
        <div className="player-buttons">
          <button 
            className={`control-btn ${shuffle ? 'active' : ''}`}
            onClick={() => setShuffle(!shuffle)}
          >
            🔀
          </button>
          <button className="control-btn" onClick={handlePrevious}>⏮️</button>
          <button className="play-btn" onClick={togglePlayPause}>
            {isPlaying ? '⏸️' : '▶️'}
          </button>
          <button className="control-btn" onClick={handleNext}>⏭️</button>
          <button 
            className={`control-btn ${repeat !== 'none' ? 'active' : ''}`}
            onClick={() => setRepeat(repeat === 'none' ? 'all' : repeat === 'all' ? 'one' : 'none')}
          >
            🔁{repeat === 'one' && '1'}
          </button>
        </div>
        
        <div className="progress-section">
          <span className="time">{formatTime(currentTime)}</span>
          <div className="progress-bar" onClick={handleSeek}>
            <div 
              className="progress-fill" 
              style={{ width: `${(currentTime / duration) * 100}%` }}
            />
          </div>
          <span className="time">{formatTime(duration)}</span>
        </div>
      </div>

      <div className="player-volume">
        <span>🔊</span>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={volume}
          onChange={(e) => setVolume(parseFloat(e.target.value))}
          className="volume-slider"
        />
      </div>
    </div>
  );
};

const SongItem = ({ song, onPlay, showArtist = true }) => {
  const { setCurrentSong, setIsPlaying, setPlaylist, setCurrentIndex } = useMusicContext();

  const handlePlay = () => {
    setCurrentSong(song);
    setPlaylist([song]);
    setCurrentIndex(0);
    setIsPlaying(true);
    if (onPlay) onPlay(song);
  };

  return (
    <div className="song-item" onClick={handlePlay}>
      <img src={song.cover_art} alt={song.title} className="song-cover" />
      <div className="song-info">
        <h4 className="song-title">{song.title}</h4>
        {showArtist && <p className="song-artist">{song.artist}</p>}
        <p className="song-details">{song.album} • {Math.floor(song.duration / 60)}:{(song.duration % 60).toString().padStart(2, '0')}</p>
      </div>
      <div className="song-actions">
        <button className="action-btn">❤️</button>
        <button className="action-btn">➕</button>
      </div>
    </div>
  );
};

const Home = () => {
  const [songs, setSongs] = useState([]);
  const [featuredPlaylists, setFeaturedPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHomeData();
  }, []);

  const fetchHomeData = async () => {
    try {
      const [songsRes, playlistsRes] = await Promise.all([
        axios.get(`${API}/songs`),
        axios.get(`${API}/playlists`)
      ]);
      
      setSongs(songsRes.data.slice(0, 6));
      setFeaturedPlaylists(playlistsRes.data.slice(0, 4));
    } catch (error) {
      console.error('Error fetching home data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">🎵 Loading your music...</div>;
  }

  return (
    <div className="main-content">
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Welcome back to StreamifyMusic</h1>
          <p className="hero-subtitle">Discover and enjoy your favorite music</p>
        </div>
        <div className="hero-image">
          <img src="https://images.unsplash.com/photo-1508898578281-774ac4893c0c" alt="Music" />
        </div>
      </div>

      <section className="music-section">
        <h2 className="section-title">Recently Played</h2>
        <div className="songs-grid">
          {songs.map(song => (
            <SongItem key={song.id} song={song} />
          ))}
        </div>
      </section>

      <section className="playlists-section">
        <h2 className="section-title">Featured Playlists</h2>
        <div className="playlists-grid">
          {featuredPlaylists.map(playlist => (
            <div key={playlist.id} className="playlist-card">
              <img src={playlist.cover_art || "https://images.pexels.com/photos/7676248/pexels-photo-7676248.jpeg"} alt={playlist.name} />
              <h4>{playlist.name}</h4>
              <p>{playlist.description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

const Search = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (searchQuery) => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(`${API}/songs/search?q=${encodeURIComponent(searchQuery)}`);
      setResults(response.data);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      handleSearch(query);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query]);

  return (
    <div className="main-content">
      <div className="search-header">
        <h1>Search</h1>
        <div className="search-box">
          <input
            type="text"
            placeholder="What do you want to listen to?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="search-input"
          />
          <span className="search-icon">🔍</span>
        </div>
      </div>

      {loading && <div className="loading">Searching...</div>}

      {results.length > 0 && (
        <div className="search-results">
          <h2>Songs</h2>
          <div className="songs-list">
            {results.map(song => (
              <SongItem key={song.id} song={song} />
            ))}
          </div>
        </div>
      )}

      {query && !loading && results.length === 0 && (
        <div className="no-results">
          <p>No results found for "{query}"</p>
        </div>
      )}
    </div>
  );
};

const Library = () => {
  const [songs, setSongs] = useState([]);
  const [artists, setArtists] = useState([]);
  const [albums, setAlbums] = useState([]);
  const [activeTab, setActiveTab] = useState('songs');

  useEffect(() => {
    fetchLibraryData();
  }, []);

  const fetchLibraryData = async () => {
    try {
      const [songsRes, artistsRes, albumsRes] = await Promise.all([
        axios.get(`${API}/songs`),
        axios.get(`${API}/artists`),
        axios.get(`${API}/albums`)
      ]);
      
      setSongs(songsRes.data);
      setArtists(artistsRes.data);
      setAlbums(albumsRes.data);
    } catch (error) {
      console.error('Error fetching library data:', error);
    }
  };

  return (
    <div className="main-content">
      <h1>Your Library</h1>
      
      <div className="library-tabs">
        <button 
          className={`tab ${activeTab === 'songs' ? 'active' : ''}`}
          onClick={() => setActiveTab('songs')}
        >
          Songs ({songs.length})
        </button>
        <button 
          className={`tab ${activeTab === 'artists' ? 'active' : ''}`}
          onClick={() => setActiveTab('artists')}
        >
          Artists ({artists.length})
        </button>
        <button 
          className={`tab ${activeTab === 'albums' ? 'active' : ''}`}
          onClick={() => setActiveTab('albums')}
        >
          Albums ({albums.length})
        </button>
      </div>

      {activeTab === 'songs' && (
        <div className="songs-list">
          {songs.map(song => (
            <SongItem key={song.id} song={song} />
          ))}
        </div>
      )}

      {activeTab === 'artists' && (
        <div className="artists-grid">
          {artists.map(artist => (
            <div key={artist.name} className="artist-card">
              <div className="artist-avatar">🎤</div>
              <h4>{artist.name}</h4>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'albums' && (
        <div className="albums-grid">
          {albums.map(album => (
            <div key={album.name} className="album-card">
              <img src={album.cover_art} alt={album.name} />
              <h4>{album.name}</h4>
              <p>{album.artist}</p>
              <p>{album.song_count} songs</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const Login = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const response = await axios.post(`${API}${endpoint}`, formData);
      onLogin(response.data);
    } catch (error) {
      console.error('Authentication error:', error);
      alert('Authentication failed. Please try again.');
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">🎵 StreamifyMusic</h1>
        <h2>{isLogin ? 'Welcome Back' : 'Join StreamifyMusic'}</h2>
        
        <form onSubmit={handleSubmit} className="login-form">
          {!isLogin && (
            <input
              type="text"
              placeholder="Username"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              required
            />
          )}
          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            required
          />
          <button type="submit" className="login-btn">
            {isLogin ? 'Sign In' : 'Sign Up'}
          </button>
        </form>
        
        <p className="login-switch">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button 
            onClick={() => setIsLogin(!isLogin)}
            className="switch-btn"
          >
            {isLogin ? 'Sign Up' : 'Sign In'}
          </button>
        </p>
      </div>
    </div>
  );
};

const App = () => {
  const [currentView, setCurrentView] = useState('home');
  const [user, setUser] = useState(null);

  // Mock user for demo - remove this in production
  useEffect(() => {
    const mockUser = { id: '1', username: 'Demo User', email: 'demo@streamify.com' };
    setUser(mockUser);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const renderContent = () => {
    switch (currentView) {
      case 'home':
        return <Home />;
      case 'search':
        return <Search />;
      case 'library':
        return <Library />;
      default:
        return <Home />;
    }
  };

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <MusicProvider>
      <div className="app">
        <Sidebar />
        <main className="main">
          {renderContent()}
        </main>
        <Player />
      </div>
    </MusicProvider>
  );
};

export default App;