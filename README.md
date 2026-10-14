# Source Sep

Upload a song, pick a section on its waveform, and split it into **vocals, drums, bass and other** stems with [Demucs](https://github.com/adefossez/demucs) (`htdemucs`).

Flask API in `backend/`, React + Vite UI in `frontend/`.

## Requirements

- [uv](https://docs.astral.sh/uv/) (`brew install uv`)
- Node 20+
- ffmpeg on your PATH (`brew install ffmpeg`), used to decode and trim uploads

## Develop

```sh
# terminal 1: API on :5001 (macOS AirPlay already holds :5000)
cd backend && uv sync && uv run flask --app app run --port 5001

# terminal 2: UI on :5173, proxies /api to the API
cd frontend && npm install && npm run dev
```

The first separation downloads the model (~80 MB). On CPU, separating takes roughly as long as the clip.

## Run without the dev server

```sh
cd frontend && npm run build
cd ../backend && uv run flask --app app run --port 5001   # open http://127.0.0.1:5001
```

## Test

```sh
cd backend && uv run pytest
```

## API

| Method | Path | Notes |
| --- | --- | --- |
| POST | `/api/jobs` | multipart `file`, optional `start`/`end` seconds. Returns `202 {id}` |
| GET | `/api/jobs/<id>` | `{status: queued, running, done or error, stems?, error?}` |
| GET | `/api/jobs/<id>/<stem>.wav` | stem is one of vocals, drums, bass, other |

Jobs live in memory with one worker and outputs land in `backend/jobs/`. A restart forgets jobs, and nothing cleans up old outputs yet.
