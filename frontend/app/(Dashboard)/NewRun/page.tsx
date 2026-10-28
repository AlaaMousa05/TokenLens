"use client";
import SideBar from "@/Components/SidBar/SideBar";
import { useState } from "react";
type InputMode = "prompt" | "dataset";
const panel = "rounded-xl border border-[#1b2750] bg-[#0c1530] p-5";
const label = "mb-1.5 block text-sm font-medium text-slate-300";
const field = "w-full rounded-lg border border-[#223062] bg-[#091129] px-3 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:border-[#4a5df0] focus:outline-none focus:ring-1 focus:ring-[#4a5df0]";
export default function NewRunPage() {
  const [mode, setMode] = useState<InputMode>("prompt");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [prompt, setPrompt] = useState("");
  return (
    <div className="min-h-screen bg-[#060b1f] text-slate-200">
      <SideBar />
      <main className="min-w-0 px-4 pb-8 pt-20 sm:ml-64 sm:px-8">
        <header className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-white">New Run</h1>
            <p className="mt-1 text-sm text-slate-400">
              Configure your test, select models and run comparisons.
            </p>
          </div>
          {/* Mode selection buttons */}
          <div role="tablist" className="flex gap-2 text-sm">
            {(["prompt", "dataset"] as const).map((m) => (
              <button
                key={m}
                role="tab"
                aria-selected={mode === m}
                onClick={() => setMode(m)}
                className={`rounded-lg px-4 py-2 font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#6b7dff] ${mode === m
                    ? "bg-[#3347e0] text-white"
                    : "border border-[#223062] bg-[#0c1530] text-slate-300 hover:bg-[#101c3f]"
                  }`}
              >
                {m === "prompt" ? "Single Prompt" : "Upload Dataset"}
              </button>
            ))}
          </div>
        </header>
        {/* Row 1: prompt / dataset  +  settings */}
        <div className="grid gap-5 lg:grid-cols-[minmax(0,1.9fr)_minmax(0,1fr)]">
          <section className={panel}>
            {mode === "prompt" && (
              <div className="space-y-3">
                <div>
                  <label htmlFor="prompt" className={label}>Your prompt</label>
                  <textarea
                    id="prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    rows={9}
                    placeholder="Enter your prompt here…"
                    className={field}
                  />
                  <p className="mt-1.5 text-right text-xs text-slate-500">{prompt.length} characters</p>
                </div>
                <div>
                  <label htmlFor="system-prompt" className={label}>System prompt (optional)</label>
                  <textarea
                    id="system-prompt"
                    value={systemPrompt}
                    onChange={(e) => setSystemPrompt(e.target.value)}
                    rows={2}
                    placeholder="e.g. You are a helpful support agent…"
                    className={field}
                  />
                </div>
              </div>
            )}
          </section>
        </div>
        {/* Row 2: model selection  +  judge configuration */}
      </main>
    </div>
  );
}