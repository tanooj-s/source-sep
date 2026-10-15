import io
import shutil
import subprocess
import time
import wave

import app as server


def make_wav(seconds=2, rate=8000):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * rate * seconds)
    return buf.getvalue()


def fake_run(cmd):
    if cmd[1:3] == ["-m", "demucs"]:  # stub the slow model, keep real ffmpeg
        out = server.JOBS_DIR / cmd[-1].split("/")[-2] / server.MODEL / "input"
        out.mkdir(parents=True)
        for stem in server.STEMS:
            shutil.copy(cmd[-1], out / f"{stem}.wav")  # silent input, so the tab step runs but finds no notes
        return subprocess.CompletedProcess(cmd, 0, "", "")
    return subprocess.run(cmd, capture_output=True, text=True)


def test_job_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(server, "run", fake_run)
    client = server.app.test_client()

    bad = client.post("/api/jobs", data={"file": (io.BytesIO(make_wav()), "a.wav"), "start": "abc"})
    assert bad.status_code == 400 and "start" in bad.json["error"]

    res = client.post("/api/jobs", data={"file": (io.BytesIO(make_wav()), "a.wav"), "start": "0.5", "end": "1.5"})
    assert res.status_code == 202
    job_id = res.json["id"]

    for _ in range(300):  # first librosa call JIT-compiles for a while
        job = client.get(f"/api/jobs/{job_id}").json
        if job["status"] in ("done", "error"):
            break
        time.sleep(0.1)
    assert job == {"status": "done", "stems": list(server.STEMS), "tab": True}, job

    with wave.open(str(tmp_path / job_id / "input.wav")) as w:  # ffmpeg trimmed to 1s
        assert abs(w.getnframes() / w.getframerate() - 1.0) < 0.05

    assert client.get(f"/api/jobs/{job_id}/vocals.wav").data[:4] == b"RIFF"
    assert "No bass notes detected" in client.get(f"/api/jobs/{job_id}/bass_tab.txt").text
    assert client.get(f"/api/jobs/{job_id}/secrets.wav").status_code == 404
