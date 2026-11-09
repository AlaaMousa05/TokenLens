"use client";

import { useState } from "react";
import { 
  BarChart2, 
  ChevronDown, 
  Search, 
  Filter, 
  ArrowUpDown,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Clock,
  DollarSign,
  Sparkles
} from "lucide-react";

export default function DetailedItemResultsPage() {
  // قائمة العناصر/الأسئلة من الـ Dataset للاختيار بينها
  const datasetItems = [
    { id: "item-1", label: "Q1: Explain quantum computing in simple terms" },
    { id: "item-2", label: "Q2: Write a Python function for binary search" },
    { id: "item-3", label: "Q3: Summarize customer support refund policies" },
  ];

  const [selectedItem, setSelectedItem] = useState(datasetItems[0].id);

  // بيانات نتائج النماذج لهذه المسألة المحددة
  const modelResults = [
    {
      id: "1",
      modelName: "GPT-4o",
      answer: "Quantum computing uses qubits that can exist in multiple states simultaneously due to superposition, allowing parallel computation...",
      score: 82.4,
      judgeReason: "Accurate explanation, clear terminology, and covers both superposition and entanglement effectively.",
      latencyMs: 842,
      cost: 0.0017,
      status: "passed",
    },
    {
      id: "2",
      modelName: "Claude 3.5 Sonnet",
      answer: "Imagine traditional computers as light switches (0 or 1). Quantum computers use qubits that can be both ON and OFF at the same time...",
      score: 87.2,
      judgeReason: "Exceptional analogy for non-technical audience. High clarity and structure.",
      latencyMs: 620,
      cost: 0.0010,
      status: "passed",
    },
    {
      id: "3",
      modelName: "Llama 3 70B",
      answer: "Quantum computing is a type of computation whose operations can harness the phenomena of quantum mechanics like superposition...",
      score: 76.5,
      judgeReason: "Factually correct but slightly too formal for a 'simple terms' prompt requirement.",
      latencyMs: 655,
      cost: 0.0004,
      status: "passed",
    },
    {
      id: "4",
      modelName: "GPT-4o-mini",
      answer: "It is a fast computer that uses quantum physics to solve hard math problems much quicker than regular laptops.",
      score: 65.2,
      judgeReason: "Over-simplified. Missed key concepts like qubits or superposition.",
      latencyMs: 320,
      cost: 0.0001,
      status: "passed",
    },
    {
      id: "5",
      modelName: "Gemini 1.5 Pro",
      answer: "Quantum computers leverage principles of quantum physics—specifically superposition and entanglement—to perform complex calculations...",
      score: 75.8,
      judgeReason: "Good depth, but slightly repetitive phrasing in the second paragraph.",
      latencyMs: 860,
      cost: 0.0008,
      status: "passed",
    },
    {
      id: "6",
      modelName: "Mistral NeMo",
      answer: "Quantum bits or qubits process complex queries simultaneously. Think of it as exploring all paths in a maze at once.",
      score: 70.5,
      judgeReason: "Decent analogy, but missed detailed explanation on superposition.",
      latencyMs: 410,
      cost: 0.0002,
      status: "passed",
    },
    {
      id: "7",
      modelName: "Llama 3 8B",
      answer: "A quantum computer is just a very powerful supercomputer that runs on special chips and cold temperatures.",
      score: 51.8,
      judgeReason: "Inaccurate distinction between supercomputers and quantum hardware.",
      latencyMs: 290,
      cost: 0.0001,
      status: "regression",
    },
  ];

  return (
    <div className="pl-72 pr-8 pt-8 pb-12 w-full min-h-screen bg-[#070b19] box-border text-slate-100 font-sans">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header Section */}
        <div className="space-y-1">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <BarChart2 className="w-7 h-7 text-indigo-400" />
            Detailed Item Results (Item-by-item Comparisons)
          </h1>
          <p className="text-sm text-slate-400">
            Select a specific item from dataset to view detailed model scores, judge reasoning, latency, and costs side-by-side.
          </p>
        </div>

        {/* Dataset Item Selector Card */}
        <div className="bg-[#0b132b] border border-slate-800/80 rounded-xl p-5 shadow-lg space-y-3">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
            Select a specific item from dataset
          </label>
          
          <div className="relative max-w-xl">
            <select
              value={selectedItem}
              onChange={(e) => setSelectedItem(e.target.value)}
              className="w-full appearance-none bg-[#070b19] border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors pr-10 cursor-pointer shadow-inner"
            >
              {datasetItems.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.label}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
          </div>
        </div>

        {/* Detailed Item Comparison Table */}
        <div className="bg-[#0b132b] border border-slate-800/80 rounded-xl overflow-hidden shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider bg-[#070b19]/60">
                  <th className="py-3.5 px-4 min-w-37.5">Model Name</th>
                  <th className="py-3.5 px-4 min-w-70">Model Answer</th>
                  <th className="py-3.5 px-4 min-w-27.5">
                    <div className="flex items-center gap-1 cursor-pointer hover:text-white">
                      <span>Model Score</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="py-3.5 px-4 min-w-65">Judge Reason</th>
                  <th className="py-3.5 px-4 min-w-35">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-400" />
                      <span>Latency / Cost</span>
                    </div>
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-800/70 text-xs">
                {modelResults.map((res) => {
                  const isHighPerformance = res.score >= 80;
                  const isLowPerformance = res.score < 60;

                  return (
                    <tr 
                      key={res.id} 
                      className={`hover:bg-slate-900/40 transition-colors ${
                        res.status === "regression" ? "bg-red-500/5" : ""
                      }`}
                    >
                      {/* Model Name */}
                      <td className="py-4 px-4 font-semibold text-white whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            isHighPerformance ? "bg-emerald-400" : isLowPerformance ? "bg-red-400" : "bg-indigo-400"
                          }`} />
                          {res.modelName}
                        </div>
                      </td>

                      {/* Model Answer */}
                      <td className="py-4 px-4 text-slate-300 leading-relaxed max-w-xs">
                        <p className="line-clamp-3 text-xs text-slate-200" title={res.answer}>
                          {res.answer}
                        </p>
                      </td>

                      {/* Score Badge */}
                      <td className="py-4 px-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold border ${
                            isHighPerformance
                              ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                              : isLowPerformance
                              ? "bg-red-500/10 text-red-400 border-red-500/20"
                              : "bg-indigo-500/10 text-indigo-300 border-indigo-500/20"
                          }`}
                        >
                          {res.score.toFixed(1)}
                        </span>
                      </td>

                      {/* Judge Reasoning */}
                      <td className="py-4 px-4 text-slate-400 text-xs leading-relaxed max-w-sm">
                        <span className="italic text-slate-300 bg-[#070b19]/40 p-2 rounded-lg block border border-slate-800/40">
                          &quot;{res.judgeReason}&quot;
                        </span>
                      </td>

                      {/* Latency & Cost */}
                      <td className="py-4 px-4 whitespace-nowrap">
                        <div className="space-y-1">
                          <div className="flex items-center gap-1 text-slate-200 font-mono text-[11px]">
                            <Clock className="w-3 h-3 text-slate-400" />
                            <span>{res.latencyMs} ms</span>
                          </div>
                          <div className="flex items-center gap-1 text-emerald-400 font-mono text-[11px]">
                            <DollarSign className="w-3 h-3 text-emerald-500" />
                            <span>${res.cost.toFixed(4)}</span>
                          </div>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}
