# Telegram Media Search + Streaming Platform

## Project Goal

Build a self-hosted web platform that indexes media from multiple Telegram database channels and allows users to:

- Search across all channels instantly
- Remove duplicate entries
- Group different qualities (480p, 720p, 1080p, 2160p)
- Group multiple languages (Hindi, English, Tamil, etc.)
- Group Dubbed/Original versions
- Display thumbnail/poster
- Stream directly over HTTP
- Download through local streaming server
- Support TV/Web/Mobile
- Very fast searching

The website should work like a personal media server powered by Telegram storage.

---

## Architecture

```text
Telegram Channels
        │
        │
Telethon Userbot Workers
        │
        ▼
Message Parser
        │
        ▼
Metadata Extractor
        │
        ▼
Duplicate Filter
        │
        ▼
HF Dataset Database
        │
        ▼
Backend API
        │
        ▼
Frontend Website
        │
        ├── Search
        ├── Details Page
        ├── Stream
        └── Download
```

---

## Tech Stack

### Backend

- Python
- FastAPI

### Telegram

- Telethon
- Multi Session Support
- Userbot + Assistant Bots

### Frontend

- React
- NextJS
- TailwindCSS

### Search

- SQLite Index
  or
- TinySearch Engine

### Storage

- HuggingFace Dataset Repository

### Hosting

- HuggingFace Docker Space

### Streaming

- FastAPI HTTP Streaming
- Range Header Support
- Resume Download Support

### Thumbnail

- Telegram Photo
  or
- TMDB Auto Fetch

---

## Telegram Indexer

Telethon should continuously scan all database channels.

Example:

- Channel1
- Channel2
- Channel3
- Anime
- Movies
- Series
- Netflix
- Prime
- Etc

Every media message should be indexed.

Supported:

- Video
- Document
- Audio
- MKV
- MP4

Ignore:

- Stickers
- Photos
- Chat messages

---

## Metadata Extraction

Automatically detect:

- Title
- Quality
- Language
- Type
- Codec
- Source
- Episode Number
- Season Number
- Release Year
- File Size
- Poster
- Thumbnail
- Message Link
- Channel ID
- Message ID
- Filename
- Mime Type

Examples:

- Titles: One Piece, Avengers Endgame, Solo Leveling
- Quality: 360p, 480p, 720p, 1080p, 2160p, 4K, HDR
- Languages: Hindi, English, Tamil, Telugu, Malayalam, Dual Audio, Multi Audio
- Type: Movie, Anime, Series, Episode, Season
- Codec: HEVC, x264, x265, AV1
- Source: WEB-DL, BluRay, HDRip, DVDRip, PreDVD, CAM

---

## Duplicate Detection

Many channels contain duplicate uploads.

Need automatic duplicate grouping.

Example:

Avengers Endgame with 480p, 720p, 1080p and 2160p should become one movie card with grouped quality variants.

Similarly, Hindi/English/Dual Audio variants should be merged under one logical title.

No duplicate cards should appear.

---

## Database Structure

```text
media/
  movie_id/
    title
    year
    poster
    description
    genre
    qualities[]
    languages[]
    versions[]
    files[]
```

Each file should contain:

- telegram_channel
- message_id
- quality
- language
- codec
- source
- size
- assistant_bot

---

## HF Dataset

Store:

- database.json
- movies.json
- anime.json
- series.json
- index.db
- thumbs/
- cache/
- sessions/

Session files:

- assistant1.session
- assistant2.session
- assistant3.session
- main.session

Sessions should load automatically.

---

## Multi Assistant Bots

Support multiple Telethon sessions.

Example workers:

- Worker1
- Worker2
- Worker3
- Worker4
- Worker5

Scheduler requirements:

- Round-robin distribution
- Automatic failover
- Automatic reconnect
- Health monitoring

---

## Search API

Endpoints:

- `/search?q=naruto`
- `/search?q=avengers`
- `/search?q=solo`

Capabilities:

- Partial search
- Fuzzy search
- Typo correction
- Ranking
- Fast response
- Pagination

---

## Details Page

Display:

- Poster
- Title
- Description
- Genres
- Year
- Runtime
- Languages
- Qualities
- Available files
- Episode list
- Season list
- Download
- Watch now

---

## Thumbnail System

Priority:

1. Telegram Thumbnail
2. TMDB Poster
3. Generated Placeholder

Cache thumbnails locally.

---

## Streaming Server

Need local HTTP streaming server with support for:

- HTTP Range
- Seek
- Resume
- Pause
- Buffer
- Progressive Streaming

Should work with:

- VLC
- MPV
- Browser
- Android
- TV

---

## Download API

Endpoint:

- `/download/id`

Requirements:

- Resume
- Range
- Fast
- Multi-thread compatible
- No Telegram redirect visible

---

## Cache System

Keep recently streamed chunks in cache.

Use LRU cache to improve repeated streams.

---

## Frontend

### Homepage

- Search Bar
- Trending
- Recently Added
- Anime
- Movies
- Series

### Search Results

- Poster
- Title
- Year
- Languages
- Qualities

### Details

- Poster
- Description
- Buttons: Watch, Download

### Player

- HTML5
- HLS
- MP4
- Seek
- Fullscreen
- Subtitle

---

## Admin Panel

Protected login.

Functions:

- Rescan Channels
- Delete Index
- Refresh Posters
- Refresh Metadata
- View Logs
- View Sessions
- Worker Status
- Rebuild Search
- Upload Session
- Channel Management
- Blacklist Messages
- Whitelist Channels

---

## Auto Scanner

Every few minutes:

- Scan channels
- Find new media
- Extract metadata
- Detect duplicates
- Update index
- Refresh search

No manual intervention required.

---

## API Endpoints

- `GET /search`
- `GET /movie/{id}`
- `GET /stream/{id}`
- `GET /download/{id}`
- `GET /thumb/{id}`
- `GET /recent`
- `GET /anime`
- `GET /movies`
- `GET /series`
- `POST /admin/rebuild`
- `POST /admin/rescan`

---

## Performance Goals

- Search: `<100ms`
- Index: incremental
- Streaming: immediate start
- Memory: low
- CPU: low
- Scalable: yes

---

## Future Features

- Subtitle support
- Continue Watching
- Watch History
- Favorites
- Watchlist
- Chromecast
- Android TV UI
- PWA Install
- Telegram Login
- QR Login
- AI Metadata Cleanup
- AI Duplicate Detection
- Smart Recommendations
- Multi-language UI
- Dark Mode
- Offline Cache

---

## Important Notes

- Never expose Telegram message links publicly.
- All streams should be proxied through the backend.
- Use asynchronous Telethon workers for maximum throughput.
- Keep HF Dataset synchronized after every index update.
- Implement proper rate limiting and retry handling for Telegram API calls.
- Separate indexing, search, and streaming into independent services for easier scaling and maintenance.
- Codebase should be modular, fully typed, and production-ready with Docker Compose support for local development and a Dockerfile for HuggingFace Spaces deployment.
