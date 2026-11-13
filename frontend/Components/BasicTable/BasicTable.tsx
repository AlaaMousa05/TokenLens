"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

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

export default function RecentRunsTable() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
          throw new Error("Failed to load recent runs.");
        }

        const data: RunsResponse = await response.json();
        setRuns(data.items || []);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Something went wrong while loading runs.",
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

  const getRunDetailsUrl = (run: Run) =>
    `/detailed-results?run_id=${encodeURIComponent(
      run.id,
    )}&dataset_id=${encodeURIComponent(run.dataset_id)}`;

  return (
    <div className="w-full bg-[#0b132b] text-slate-300 p-6 rounded-xl border border-slate-800/80 font-sans shadow-xl">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-white">Recent Runs</h2>
        <Link
          href="/runhistory"
          className="text-sm text-blue-400 hover:underline"
        >
          View all
        </Link>
      </div>

      {/* Loading */}
      {loading && (
        <div className="py-10 text-center text-sm text-slate-400">
          Loading recent runs...
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="py-10 text-center text-sm text-rose-400">{error}</div>
      )}

      {/* Table */}
      {!loading && !error && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left border-collapse">
            <thead>
              <tr className="text-slate-400 border-b border-slate-800/60 text-xs">
                <th className="pb-3 font-normal">Name</th>
                <th className="pb-3 font-normal">Models</th>
                <th className="pb-3 font-normal">Status</th>
                <th className="pb-3 font-normal">Avg. Score</th>
                <th className="pb-3 font-normal">Total Cost</th>
                <th className="pb-3 font-normal">Created At</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-800/40">
              {runs.length > 0 ? (
                runs.map((row) => (
                  <tr
                    key={row.id}
                    onClick={() => {
                      window.location.href = getRunDetailsUrl(row);
                    }}
                    className="hover:bg-slate-800/40 transition-colors cursor-pointer"
                    title="View run details"
                  >
                    <td className="py-4 pr-4 font-medium text-slate-200">
                      <Link
                        href={getRunDetailsUrl(row)}
                        onClick={(event) => event.stopPropagation()}
                        className="flex items-center gap-3 hover:text-blue-400 transition-colors"
                      >
                        <div className="w-5 h-5 rounded bg-blue-600 flex items-center justify-center text-[10px] text-white font-bold">
                          ||
                        </div>

                        <span>{row.name}</span>
                      </Link>
                    </td>

                    <td className="py-4 px-2 text-slate-400">
                      {row.model_ids?.length
                        ? `${row.model_ids.length} ${
                            row.model_ids.length === 1 ? "model" : "models"
                          }`
                        : "—"}
                    </td>

                    <td className="py-4 px-2">
                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border ${getStatusStyle(
                          row.status,
                        )}`}
                      >
                        {row.status}
                      </span>
                    </td>

                    <td className="py-4 px-2 text-slate-400">—</td>

                    <td className="py-4 px-2 text-slate-300 font-medium">
                      {formatCost(row.total_cost_usd)}
                    </td>

                    <td className="py-4 px-2 text-slate-400 text-xs">
                      {formatDate(row.created_at)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-10 text-center text-slate-400">
                    No runs found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
