
"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  History,
  Search,
  Clock,
  DollarSign,
  ArrowUpRight,
} from "lucide-react";

interface Run {
  id: string;
  dataset_id: string;
  name: string;
  status: string;
  total_cost_usd: string;
  created_at: string;
  model_ids: string[];
}

interface RunsResponse {
  items: Run[];
  page: number;
  size: number;
  total: number;
}

export default function RunHistoryPage() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    const fetchRuns = async () => {
      try {
        const token =
          localStorage.getItem("access_token") ||
          sessionStorage.getItem("access_token");

        const API_URL =
          process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

        const response = await fetch(`${API_URL}/runs`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        });

        if (response.status === 401) {
          localStorage.removeItem("access_token");
          sessionStorage.removeItem("access_token");
          window.location.href = "/";
          return;
        }

        if (!response.ok) {
          throw new Error("Failed to load run history.");
        }

        const data: RunsResponse = await response.json();
        setRuns(data.items || []);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Something went wrong while loading runs."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchRuns();
  }, []);

  const getStatusStyle = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
      case "succeeded":
        return "bg-emerald-950/60 text-emerald-400 border-emerald-800/40";
      case "failed":
        return "bg-rose-950/60 text-rose-400 border-rose-800/40";
      case "running":
        return "bg-blue-950/60 text-blue-400 border-blue-800/40";
      case "queued":
        return "bg-amber-950/60 text-amber-400 border-amber-800/40";
      default:
        return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  const formatDate = (date: string) => {
    if (!date) return "—";

    return new Date(date).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  };

  const formatCost = (cost: string) => {
    const value = Number(cost);
    return Number.isFinite(value) ? `$${value.toFixed(4)}` : "—";
  };

  const filteredRuns = runs.filter((run) =>
    run.name.toLowerCase().includes(search.toLowerCase())
  );

  const getRunDetailsUrl = (run: Run) =>
    `/detailed-results?run_id=${encodeURIComponent(
      run.id
    )}&dataset_id=${encodeURIComponent(run.dataset_id)}`;

  return (
    <div className="pl-72 pr-8 pt-8 pb-12 w-full min-h-screen bg-[#070b19] box-border text-slate-100 font-sans">
      <div className="max-w-7xl mx-auto space-y-6">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <History className="w-7 h-7 text-indigo-400" />
              Run History
            </h1>
            <p className="text-sm text-slate-400 mt-2">
              View and manage all your previous evaluation runs.
            </p>
          </div>

          <div className="bg-[#0b132b] border border-slate-800 rounded-lg px-4 py-2">
            <p className="text-xs text-slate-400">Total Runs</p>
            <p className="text-xl font-bold text-white">{runs.length}</p>
          </div>
        </div>

        {/* Search */}
        <div className="bg-[#0b132b] border border-slate-800/80 rounded-xl p-4">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search runs by name..."
              className="w-full bg-[#070b19] border border-slate-800 rounded-lg py-2.5 pl-10 pr-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="bg-[#0b132b] border border-slate-800/80 rounded-xl p-10 text-center text-sm text-slate-400">
            Loading run history...
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="bg-[#0b132b] border border-red-900/50 rounded-xl p-10 text-center text-sm text-red-400">
            {error}
          </div>
        )}

        {/* Table */}
        {!loading && !error && (
          <div className="bg-[#0b132b] text-slate-300 rounded-xl border border-slate-800/80 shadow-xl overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b border-slate-800/60">
              <div>
                <h2 className="text-lg font-semibold text-white">
                  All Evaluation Runs
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  {filteredRuns.length} runs found
                </p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left border-collapse">
                <thead>
                  <tr className="text-slate-400 border-b border-slate-800/60 text-xs">
                    <th className="py-4 px-6 font-normal">Name</th>
                    <th className="py-4 px-4 font-normal">Models</th>
                    <th className="py-4 px-4 font-normal">Status</th>
                    <th className="py-4 px-4 font-normal">Total Cost</th>
                    <th className="py-4 px-4 font-normal">Created At</th>
                    <th className="py-4 px-6 font-normal text-right">Details</th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-800/40">
                  {filteredRuns.length > 0 ? (
                    filteredRuns.map((run) => (
                      <tr
                        key={run.id}
                        onClick={() => {
                          window.location.href = getRunDetailsUrl(run);
                        }}
                        className="hover:bg-slate-800/40 transition-colors cursor-pointer"
                      >
                        <td className="py-4 px-6 font-medium text-slate-200">
                          {run.name}
                        </td>

                        <td className="py-4 px-4 text-slate-400">
                          {run.model_ids?.length
                            ? `${run.model_ids.length} ${
                                run.model_ids.length === 1 ? "model" : "models"
                              }`
                            : "—"}
                        </td>

                        <td className="py-4 px-4">
                          <span
                            className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border ${getStatusStyle(
                              run.status
                            )}`}
                          >
                            {run.status}
                          </span>
                        </td>

                        <td className="py-4 px-4 text-slate-300 font-medium">
                          {formatCost(run.total_cost_usd)}
                        </td>

                        <td className="py-4 px-4 text-slate-400 text-xs whitespace-nowrap">
                          {formatDate(run.created_at)}
                        </td>

                        <td className="py-4 px-6 text-right">
                          <Link
                            href={getRunDetailsUrl(run)}
                            onClick={(event) => event.stopPropagation()}
                            className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300"
                          >
                            View Details
                            <ArrowUpRight className="w-4 h-4" />
                          </Link>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td
                        colSpan={6}
                        className="py-10 text-center text-slate-400"
                      >
                        {search
                          ? "No runs match your search."
                          : "No runs found."}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
