# Source Sep

Upload a song (the whole track, or a section picked on its waveform) and split it into **vocals, drums, bass and other** stems with [Demucs](https://github.com/adefossez/demucs) (`htdemucs`). The bass stem is then transcribed into ASCII tab for a 4-string bass in standard tuning (`backend/tab.py`: librosa pYIN for pitch, onsets for note starts, beat tracking for the 16th-note grid).

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

The first separation downloads the model (~80 MB). The tab step assumes 4/4 with the first detected beat as a downbeat, so bar lines can be off by a beat or two. Fret choice is greedy (stays near the last fretted position, open strings preferred).

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
| GET | `/api/jobs/<id>` | `{status: queued, running, done or error, stems?, tab?, tab_error?, error?}` |
| GET | `/api/jobs/<id>/<stem>.wav` | stem is one of vocals, drums, bass, other |
| GET | `/api/jobs/<id>/bass_tab.txt` | ASCII bass tab of the whole separated audio |

Jobs live in memory with one worker and outputs land in `backend/jobs/`. A restart forgets jobs, and nothing cleans up old outputs yet.
