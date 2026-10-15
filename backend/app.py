import subprocess
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory

import tab

JOBS_DIR = Path(__file__).parent / "jobs"
DIST_DIR = Path(__file__).parent.parent / "frontend" / "dist"
MODEL = "htdemucs"
STEMS = ("vocals", "drums", "bass", "other")

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

# ponytail: in-memory job dict + 1 worker; lost on restart, swap for RQ/Celery if hosted
jobs = {}
executor = ThreadPoolExecutor(max_workers=1)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def separate(job_id, src, start, end):
    job = jobs[job_id]
    job["status"] = "running"
    jobdir = src.parent
    # Always decode through ffmpeg: trims the region and normalizes any format to WAV.
    wav = jobdir / "input.wav"
    trim = (["-ss", str(start)] if start is not None else []) + (
        ["-to", str(end)] if end is not None else []
    )
    steps = [
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), *trim, str(wav)],
        [sys.executable, "-m", "demucs", "-n", MODEL, "-o", str(jobdir), str(wav)],
    ]
    for cmd in steps:
        try:
            result = run(cmd)
        except OSError as e:  # e.g. ffmpeg not installed
            job.update(status="error", error=str(e))
            return
        if result.returncode != 0:
            job.update(status="error", error="\n".join(result.stderr.strip().splitlines()[-5:]))
            return
    try:
        (jobdir / "bass_tab.txt").write_text(tab.transcribe(jobdir / MODEL / "input" / "bass.wav", wav))
        job["tab"] = True
    except Exception as e:  # the stems are still worth returning without a tab
        job["tab_error"] = str(e)
    job["status"] = "done"
    job["stems"] = list(STEMS)


def parse_time(name):
    value = request.form.get(name, "").strip()
    if not value:
        return None
    try:
        t = float(value)
    except ValueError:
        abort(400, f"{name} must be a number of seconds")
    if t < 0:
        abort(400, f"{name} must be >= 0")
    return t


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(413)
def json_error(e):
    return jsonify(error=e.description), e.code


@app.post("/api/jobs")
def create_job():
    file = request.files.get("file")
    if not file or not file.filename:
        abort(400, "no file uploaded")
    start, end = parse_time("start"), parse_time("end")
    if start is not None and end is not None and end <= start:
        abort(400, "end must be after start")

    job_id = uuid.uuid4().hex
    jobdir = JOBS_DIR / job_id
    jobdir.mkdir(parents=True)
    src = jobdir / ("upload" + Path(file.filename).suffix.lower()[:8])
    file.save(src)

    jobs[job_id] = {"status": "queued"}
    executor.submit(separate, job_id, src, start, end)
    return jsonify(id=job_id), 202


@app.get("/api/jobs/<job_id>")
def get_job(job_id):
    if job_id not in jobs:
        abort(404, "unknown job")
    return jsonify(jobs[job_id])


@app.get("/api/jobs/<job_id>/<stem>.wav")
def get_stem(job_id, stem):
    if jobs.get(job_id, {}).get("status") != "done" or stem not in STEMS:
        abort(404, "stem not found")
    return send_from_directory(JOBS_DIR / job_id / MODEL / "input", f"{stem}.wav")


@app.get("/api/jobs/<job_id>/bass_tab.txt")
def get_tab(job_id):
    if not jobs.get(job_id, {}).get("tab"):
        abort(404, "tab not found")
    return send_from_directory(JOBS_DIR / job_id, "bass_tab.txt")


@app.get("/")
@app.get("/<path:path>")
def frontend(path="index.html"):
    if not (DIST_DIR / path).is_file():
        path = "index.html"
    return send_from_directory(DIST_DIR, path)
