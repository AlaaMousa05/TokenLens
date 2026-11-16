
"use client";

import React, { useEffect, useMemo, useState } from "react";
import {
  BarChart2,
  ChevronDown,
  ArrowUpDown,
  Clock,
  DollarSign,
} from "lucide-react";
import { base_usrl } from "@/lib/base-url";

interface DatasetItem {
  id: string;
  position: number;
  input: string;
  expected_output?: string | null;
}

interface DatasetItemsResponse {
  items: DatasetItem[];
}

interface Judgment {
  id: string;
  score: string;
  criteria_scores: Record<string, unknown>;
  reasoning: string;
  judge_cost_usd: string;
}

interface RunResult {
  id: string;
  item_id: string;
  question_text: string;
  position: number;
  model_id: string;
  model_display_name: string;
  repeat_index: number;
  output_text: string;
  input_tokens: number;
  output_tokens: number;
  latency_ms: number;
  cost_usd: string;
  status: string;
  error_message: string | null;
  attempts: number;
  judgments: Judgment[];
}

interface ResultsResponse {
  items: RunResult[];
}

export default function DetailedItemResultsPage() {
  const [datasetItems, setDatasetItems] = useState<DatasetItem[]>([]);
  const [results, setResults] = useState<RunResult[]>([]);
  const [selectedItem, setSelectedItem] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const params = new URLSearchParams(window.location.search);

        const runId = params.get("run_id");
        const datasetId = params.get("dataset_id");

        if (!runId || !datasetId) {
          throw new Error(
            "Missing run_id or dataset_id in the page URL."
          );
        }

        const token =
          localStorage.getItem("access_token") ||
          sessionStorage.getItem("access_token");

        const API_URL = base_usrl;

        const headers = {
          "Content-Type": "application/json",
          ...(token
            ? { Authorization: `Bearer ${token}` }
            : {}),
        };

        const [datasetResponse, resultsResponse] =
          await Promise.all([
            fetch(`${API_URL}/datasets/${datasetId}/items`, {
              method: "GET",
              headers,
            }),

            fetch(`${API_URL}/runs/${runId}/results`, {
              method: "GET",
              headers,
            }),
          ]);

        if (
          datasetResponse.status === 401 ||
          resultsResponse.status === 401
        ) {
          localStorage.removeItem("access_token");
          sessionStorage.removeItem("access_token");
          window.location.href = "/";
          return;
        }

        if (!datasetResponse.ok) {
          throw new Error("Failed to load dataset items.");
        }

        if (!resultsResponse.ok) {
          throw new Error("Failed to load run results.");
        }

        const datasetData: DatasetItemsResponse =
          await datasetResponse.json();

        const resultsData: ResultsResponse =
          await resultsResponse.json();

        const loadedItems = datasetData.items || [];
        const loadedResults = resultsData.items || [];

        setDatasetItems(loadedItems);
        setResults(loadedResults);

        if (loadedItems.length > 0) {
          setSelectedItem(loadedItems[0].id);
        } else if (loadedResults.length > 0) {
          setSelectedItem(loadedResults[0].item_id);
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Something went wrong while loading results."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Results belonging to the selected dataset item
  const modelResults = useMemo(() => {
    return results.filter(
      (result) => result.item_id === selectedItem
    );
  }, [results, selectedItem]);

  // Create dropdown options from dataset items
  const itemOptions = useMemo(() => {
    if (datasetItems.length > 0) {
      return datasetItems.map((item) => ({
        id: item.id,
        label: `Q${item.position + 1}: ${item.input}`,
      }));
    }

    // Fallback in case the dataset endpoint returns no items
    const uniqueItems = new Map<string, string>();

    results.forEach((result) => {
      if (!uniqueItems.has(result.item_id)) {
        uniqueItems.set(
          result.item_id,
          result.question_text || `Question ${result.position + 1}`
        );
      }
    });

    return Array.from(uniqueItems.entries()).map(
      ([id, label]) => ({
        id,
        label,
      })
    );
  }, [datasetItems, results]);

  const formatCost = (cost: string) => {
    const value = Number(cost);

    return Number.isFinite(value)
      ? `$${value.toFixed(4)}`
      : "—";
  };

  const formatScore = (score?: string) => {
    if (score === undefined || score === null || score === "") {
      return null;
    }

    const value = Number(score);

    return Number.isFinite(value) ? value : null;
  };

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
            Select a specific item from dataset to view detailed
            model scores, judge reasoning, latency, and costs
            side-by-side.
          </p>
        </div>

        {/* Loading */}
        {loading && (
          <div className="bg-[#0b132b] border border-slate-800/80 rounded-xl p-10 text-center text-sm text-slate-400">
            Loading results...
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="bg-[#0b132b] border border-red-900/50 rounded-xl p-10 text-center text-sm text-red-400">
            {error}
          </div>
        )}

        {!loading && !error && (
          <>
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
                  {itemOptions.map((item) => (
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
                      <th className="py-3.5 px-4 min-w-37.5">
                        Model Name
                      </th>

                      <th className="py-3.5 px-4 min-w-70">
                        Model Answer
                      </th>

                      <th className="py-3.5 px-4 min-w-27.5">
                        <div className="flex items-center gap-1 cursor-pointer hover:text-white">
                          <span>Model Score</span>
                          <ArrowUpDown className="w-3 h-3" />
                        </div>
                      </th>

                      <th className="py-3.5 px-4 min-w-65">
                        Judge Reason
                      </th>

                      <th className="py-3.5 px-4 min-w-35">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3 text-slate-400" />
                          <span>Latency / Cost</span>
                        </div>
                      </th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-800/70 text-xs">
                    {modelResults.length > 0 ? (
                      modelResults.map((res) => {
                        const score = formatScore(
                          res.judgments?.[0]?.score
                        );

                        const isHighPerformance =
                          score !== null && score >= 80;

                        const isLowPerformance =
                          score !== null && score < 60;

                        return (
                          <tr
                            key={res.id}
                            className="hover:bg-slate-900/40 transition-colors"
                          >
                            {/* Model Name */}
                            <td className="py-4 px-4 font-semibold text-white whitespace-nowrap">
                              <div className="flex items-center gap-2">
                                <div
                                  className={`w-2 h-2 rounded-full ${
                                    isHighPerformance
                                      ? "bg-emerald-400"
                                      : isLowPerformance
                                      ? "bg-red-400"
                                      : "bg-indigo-400"
                                  }`}
                                />

                                {res.model_display_name || "Unknown Model"}

                                {res.repeat_index > 0 && (
                                  <span className="text-slate-500 text-[10px]">
                                    (Repeat {res.repeat_index + 1})
                                  </span>
                                )}
                              </div>
                            </td>

                            {/* Model Answer */}
                            <td className="py-4 px-4 text-slate-300 leading-relaxed max-w-xs">
                              <p
                                className="line-clamp-3 text-xs text-slate-200"
                                title={res.output_text}
                              >
                                {res.output_text ||
                                  res.error_message ||
                                  "No output available."}
                              </p>
                            </td>

                            {/* Score Badge */}
                            <td className="py-4 px-4 whitespace-nowrap">
                              {score !== null ? (
                                <span
                                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold border ${
                                    isHighPerformance
                                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                                      : isLowPerformance
                                      ? "bg-red-500/10 text-red-400 border-red-500/20"
                                      : "bg-indigo-500/10 text-indigo-300 border-indigo-500/20"
                                  }`}
                                >
                                  {score.toFixed(1)}
                                </span>
                              ) : (
                                <span className="text-slate-500">
                                  —
                                </span>
                              )}
                            </td>

                            {/* Judge Reasoning */}
                            <td className="py-4 px-4 text-slate-400 text-xs leading-relaxed max-w-sm">
                              <span className="italic text-slate-300 bg-[#070b19]/40 p-2 rounded-lg block border border-slate-800/40">
                                {res.judgments?.[0]?.reasoning
                                  ? `"${res.judgments[0].reasoning}"`
                                  : res.error_message ||
                                    "No judge feedback available."}
                              </span>
                            </td>

                            {/* Latency & Cost */}
                            <td className="py-4 px-4 whitespace-nowrap">
                              <div className="space-y-1">
                                <div className="flex items-center gap-1 text-slate-200 font-mono text-[11px]">
                                  <Clock className="w-3 h-3 text-slate-400" />
                                  <span>
                                    {res.latency_ms ?? "—"} ms
                                  </span>
                                </div>

                                <div className="flex items-center gap-1 text-emerald-400 font-mono text-[11px]">
                                  <DollarSign className="w-3 h-3 text-emerald-500" />
                                  <span>
                                    {formatCost(res.cost_usd)}
                                  </span>
                                </div>
                              </div>
                            </td>
                          </tr>
                        );
                      })
                    ) : (
                      <tr>
                        <td
                          colSpan={5}
                          className="py-10 text-center text-slate-400"
                        >
                          No results found for this item.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
