"use client";
import { useEffect, useRef, useState } from "react";
import useSWR from "swr";

async function fetcher(url: string) {
  const res = await fetch(url);
  return res.json();
}

export default function Job({ params }: { params: { id: string } }) {
  const { data: log } = useSWR(`http://127.0.0.1:8000/decision_log/${params.id}`, fetcher, { refreshInterval: 3000 });
  const [latest, setLatest] = useState<any | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/${params.id}`);
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);
      setLatest(msg);
    };
    return () => {
      ws.close();
    };
  }, [params.id]);

  const entries: any[] = (log ?? []);
  if (latest) entries.push(latest);

  return (
    <main className="p-6 max-w-6xl mx-auto grid grid-cols-2 gap-6">
      <div className="bg-black aspect-video rounded flex items-center justify-center overflow-hidden">
        {latest?.overlay_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={`http://127.0.0.1:8000${latest.overlay_url}`} alt="overlay" className="w-full h-full object-contain" />
        ) : (
          <div className="text-white text-sm opacity-60">Waiting for frames…</div>
        )}
      </div>
      <div>
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold mb-2">Decision Feed</h2>
          <a className="px-3 py-2 text-sm rounded bg-gray-200" href={`http://127.0.0.1:8000/download_log/${params.id}`} target="_blank" rel="noreferrer">Download Log</a>
        </div>
        <div className="space-y-3">
          {entries.slice().reverse().map((entry: any, idx: number) => (
            <div key={idx} className="border rounded p-3 bg-white">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Frame {entry.frame_id}</span>
                <span className="px-2 py-1 text-xs rounded bg-blue-600 text-white">{entry.final_decision}</span>
              </div>
              <div className="mt-2 text-sm text-gray-700">{entry.perception_summary}</div>
              <div className="mt-2 text-xs text-gray-500">Rules: {entry.symbolic_flags?.join(", ") || "-"}</div>
              <details className="mt-2 text-xs">
                <summary>LLM JSON</summary>
                <pre className="overflow-auto bg-gray-50 p-2 rounded text-[10px]">{JSON.stringify(entry.llm_response, null, 2)}</pre>
              </details>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

