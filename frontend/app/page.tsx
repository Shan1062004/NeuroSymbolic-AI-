"use client";
import { useState } from "react";
import useSWR from "swr";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export default function Page() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [samples, setSamples] = useState<string[]>([]);
  const [selectedSample, setSelectedSample] = useState<string>("");
  const [ethicalMode, setEthicalMode] = useState<string>("Hybrid");
  const [yoloDevice, setYoloDevice] = useState<string>("cpu");

  const { data: status } = useSWR(jobId ? `http://127.0.0.1:8000/job_status/${jobId}` : null, fetcher, { refreshInterval: 1000 });

  async function loadSamples() {
    const res = await fetch("http://127.0.0.1:8000/samples");
    const j = await res.json();
    setSamples(j.samples || []);
  }

  async function onUpload() {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    const res = await fetch("http://127.0.0.1:8000/upload_video", { method: "POST", body: form });
    const json = await res.json();
    setJobId(json.job_id);
    await fetch(`http://127.0.0.1:8000/process/${json.job_id}?mode=${encodeURIComponent(ethicalMode)}&device=${encodeURIComponent(yoloDevice)}`, { method: "POST" });
  }

  return (
    <main className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">NSEthics-AV Dashboard</h1>
      <div className="border rounded p-4 bg-white">
        <div className="flex items-center gap-3">
          <input type="file" accept="video/mp4" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          <button onClick={onUpload} className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50" disabled={!file}>Upload & Process</button>
        </div>
        <div className="mt-4 flex items-center gap-3">
          <button onClick={loadSamples} className="px-3 py-2 bg-gray-200 rounded">Load Samples</button>
          <select value={selectedSample} onChange={(e) => setSelectedSample(e.target.value)} className="border rounded px-2 py-2">
            <option value="">Select a sample</option>
            {samples.map((s) => (<option key={s} value={s}>{s}</option>))}
          </select>
          <span className="text-sm text-gray-500 ml-4">Ethical Mode</span>
          <select value={ethicalMode} onChange={(e) => setEthicalMode(e.target.value)} className="border rounded px-2 py-2">
            {['Utilitarian','Deontological','Legal','Hybrid'].map(m => (<option key={m} value={m}>{m}</option>))}
          </select>
          <span className="text-sm text-gray-500 ml-2">YOLO Device</span>
          <select value={yoloDevice} onChange={(e) => setYoloDevice(e.target.value)} className="border rounded px-2 py-2">
            {['cpu','cuda'].map(d => (<option key={d} value={d}>{d}</option>))}
          </select>
          <button onClick={async () => {
            if (!selectedSample) return;
            const res = await fetch(`http://127.0.0.1:8000/start_sample/${selectedSample}`, { method: "POST" });
            const j = await res.json();
            setJobId(j.job_id);
            await fetch(`http://127.0.0.1:8000/process/${j.job_id}?mode=${encodeURIComponent(ethicalMode)}&device=${encodeURIComponent(yoloDevice)}`, { method: "POST" });
          }} className="px-4 py-2 bg-emerald-600 text-white rounded disabled:opacity-50" disabled={!selectedSample}>Use Sample & Process</button>
        </div>
        {jobId && (
          <div className="mt-4">
            <div className="text-sm text-gray-600">Job ID: {jobId}</div>
            <div className="mt-1">Status: {status?.status ?? "..."}</div>
            <a className="mt-2 inline-block text-blue-600 underline" href={`/job/${jobId}`} target="_blank" rel="noreferrer">Open Live View</a>
          </div>
        )}
      </div>
    </main>
  );
}
