"use client";
import useSWR from "swr";
import { useSearchParams } from "next/navigation";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export default function JobPage() {
  const params = useSearchParams();
  const id = params.get("id");
  const { data: log } = useSWR(id ? `http://127.0.0.1:8000/decision_log/${id}` : null, fetcher, { refreshInterval: 1000 });

  return (
    <main className="p-6 max-w-6xl mx-auto grid grid-cols-2 gap-6">
      <div className="bg-black aspect-video rounded" />
      <div>
        <h2 className="text-xl font-semibold mb-2">Decision Feed</h2>
        <div className="space-y-3">
          {(log ?? []).slice().reverse().map((entry: any, idx: number) => (
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

