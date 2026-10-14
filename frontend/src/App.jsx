import { useEffect, useRef, useState } from 'react'
import WaveSurfer from 'wavesurfer.js'
import RegionsPlugin from 'wavesurfer.js/dist/plugins/regions.esm.js'

const DEFAULT_REGION_SECONDS = 30
// Canvas can't read CSS variables, so the waveform colors are fixed mid-tones that read on light and dark.
const WAVE = { waveColor: '#8b8fa8', progressColor: '#7c5cff', height: 80 }

function useWaveSurfer(url, withRegions = false) {
  const container = useRef(null)
  const [ws, setWs] = useState(null)
  const [regions, setRegions] = useState(null)
  const [playing, setPlaying] = useState(false)

  useEffect(() => {
    if (!url) return
    const plugin = withRegions ? RegionsPlugin.create() : null
    const instance = WaveSurfer.create({ container: container.current, url, ...WAVE, plugins: plugin ? [plugin] : [] })
    instance.on('play', () => setPlaying(true))
    instance.on('pause', () => setPlaying(false))
    setWs(instance)
    setRegions(plugin)
    return () => {
      instance.destroy()
      setWs(null)
      setPlaying(false)
    }
  }, [url, withRegions])

  return { container, ws, regions, playing }
}

function Picker({ file, region, setRegion }) {
  const [url, setUrl] = useState(null)
  const { container, ws, regions, playing } = useWaveSurfer(url, true)

  useEffect(() => {
    const u = URL.createObjectURL(file)
    setUrl(u)
    return () => URL.revokeObjectURL(u)
  }, [file])

  useEffect(() => {
    if (!ws || !regions) return
    const plugin = regions
    const onDecode = (duration) => {
      plugin.clearRegions()
      const r = plugin.addRegion({
        start: 0,
        end: Math.min(DEFAULT_REGION_SECONDS, duration),
        color: 'var(--region)',
      })
      setRegion({ start: r.start, end: r.end })
    }
    ws.on('decode', onDecode)
    const off = plugin.on('region-updated', (r) => setRegion({ start: r.start, end: r.end }))
    return () => {
      ws.un('decode', onDecode)
      off()
    }
  }, [ws, regions, setRegion])

  const playRegion = () => {
    const r = regions?.getRegions()[0]
    if (playing) ws.pause()
    else if (r) r.play()
    else ws.play()
  }

  return (
    <section>
      <div ref={container} className="wave" />
      <div className="row">
        <button type="button" onClick={playRegion} disabled={!ws}>
          {playing ? 'Pause' : 'Play selection'}
        </button>
        {region && (
          <span className="muted">
            {region.start.toFixed(1)}s – {region.end.toFixed(1)}s ({(region.end - region.start).toFixed(1)}s). Drag the
            edges to change it.
          </span>
        )}
      </div>
    </section>
  )
}

function Stem({ name, url }) {
  const { container, ws, playing } = useWaveSurfer(url)
  return (
    <section className="stem">
      <div className="row">
        <h3>{name}</h3>
        <button type="button" onClick={() => ws?.playPause()} disabled={!ws}>
          {playing ? 'Pause' : 'Play'}
        </button>
        <a href={url} download={`${name}.wav`}>
          Download
        </a>
      </div>
      <div ref={container} className="wave" />
    </section>
  )
}

export default function App() {
  const [file, setFile] = useState(null)
  const [region, setRegion] = useState(null)
  const [job, setJob] = useState(null) // { id, status, stems?, error? }
  const [error, setError] = useState(null)
  const [elapsed, setElapsed] = useState(0)

  const busy = job && (job.status === 'queued' || job.status === 'running')

  useEffect(() => {
    if (!busy) return
    const started = Date.now()
    const timer = setInterval(async () => {
      setElapsed(Math.round((Date.now() - started) / 1000))
      try {
        const res = await fetch(`/api/jobs/${job.id}`)
        const data = await res.json()
        if (!res.ok) throw new Error(data.error)
        setJob((j) => ({ ...j, ...data }))
      } catch (e) {
        setError(`Lost track of the job: ${e.message}`)
        setJob(null)
      }
    }, 2000)
    return () => clearInterval(timer)
  }, [busy, job?.id])

  const submit = async (e) => {
    e.preventDefault()
    setError(null)
    const form = new FormData()
    form.append('file', file)
    if (region) {
      form.append('start', region.start.toFixed(2))
      form.append('end', region.end.toFixed(2))
    }
    try {
      const res = await fetch('/api/jobs', { method: 'POST', body: form })
      const data = await res.json().catch(() => ({ error: `Server error ${res.status}` }))
      if (!res.ok) throw new Error(data.error)
      setElapsed(0)
      setJob({ id: data.id, status: 'queued' })
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <main>
      <h1>Source Separation</h1>
      <p className="muted">
        Upload a song, pick a section, and split it into vocals, drums, bass and other with Demucs.
      </p>

      <form onSubmit={submit}>
        <label className="file">
          <span>Audio file</span>
          <input
            type="file"
            accept="audio/*"
            onChange={(e) => {
              setFile(e.target.files[0] ?? null)
              setRegion(null)
              setJob(null)
              setError(null)
            }}
          />
        </label>
        {file && <Picker file={file} region={region} setRegion={setRegion} />}
        <button type="submit" className="primary" disabled={!file || busy}>
          {busy ? 'Separating…' : 'Separate'}
        </button>
      </form>

      {error && <p className="error" role="alert">{error}</p>}
      {busy && (
        <p className="muted" aria-live="polite">
          {job.status === 'queued' ? 'Queued' : 'Separating'}… {elapsed}s. On CPU this takes roughly as long as
          the clip itself, and the first run also downloads the model.
        </p>
      )}
      {job?.status === 'error' && (
        <pre className="error" role="alert">
          {job.error}
        </pre>
      )}
      {job?.status === 'done' &&
        job.stems.map((s) => <Stem key={s} name={s} url={`/api/jobs/${job.id}/${s}.wav`} />)}
    </main>
  )
}
