"use client";
import SideBar from "@/Components/SidBar/SideBar";
import { useState } from "react";
type InputMode = "prompt" | "dataset";
const panel = "rounded-xl border border-[#1b2750] bg-[#0c1530] p-5";
const label = "mb-1.5 block text-sm font-medium text-slate-300";
const field ="w-full rounded-lg border border-[#223062] bg-[#091129] px-3 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:border-[#4a5df0] focus:outline-none focus:ring-1 focus:ring-[#4a5df0]";
export default function NewRunPage() {
  const [mode, setMode] = useState<InputMode>("prompt");
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
                className={`rounded-lg px-4 py-2 font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#6b7dff] ${
                  mode === m
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
        {/* Row 2: model selection  +  judge configuration */}
      </main>
    </div>
  );
}