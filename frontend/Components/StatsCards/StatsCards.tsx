
"use client";

import React, { useEffect, useState } from "react";
import StatCard, { StatCardProps } from "../StatCard/StatCard";
import {
  TrendingUp,
  CalendarDays,
  CircleArrowOutUpLeft,
  Star,
} from "lucide-react";

interface Run {
  id: string;
  status: string;
  total_cost_usd: string | number;
}

interface Judgment {
  score: string | number;
}

interface RunResult {
  latency_ms: number;
  status: string;
  judgments?: Judgment[];
}

interface StatsData {
  totalRuns: number;
  totalCost: number;
  avgLatency: number | null;
  avgQuality: number | null;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function StatsCards() {
  const [stats, setStats] = useState<StatsData>({
    totalRuns: 0,
    totalCost: 0,
    avgLatency: null,
    avgQuality: null,
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function fetchStats() {
      try {
        const token =
          localStorage.getItem("access_token") ||
          sessionStorage.getItem("access_token");

        if (!token) {
          window.location.href = "/";
          return;
        }

        const headers = {
          Authorization: `Bearer ${token}`,
        };

        const runsResponse = await fetch(`${API_URL}/runs`, {
          headers,
          cache: "no-store",
        });

        if (runsResponse.status === 401) {
          localStorage.removeItem("access_token");
          sessionStorage.removeItem("access_token");
          window.location.href = "/";
          return;
        }

        if (!runsResponse.ok) {
          throw new Error("Failed to fetch runs");
        }

        const runsData = await runsResponse.json();
        const runs: Run[] = runsData.items || [];

        const totalRuns = runsData.total ?? runs.length;

        const totalCost = runs.reduce(
          (sum, run) => sum + Number(run.total_cost_usd || 0),
          0
        );

        const completedRuns = runs.filter((run) =>
          ["completed", "succeeded"].includes(run.status?.toLowerCase())
        );

        const resultsResponses = await Promise.all(
          completedRuns.map(async (run) => {
            const response = await fetch(
              `${API_URL}/runs/${run.id}/results`,
              {
                headers,
                cache: "no-store",
              }
            );

            if (response.status === 401) {
              localStorage.removeItem("access_token");
              sessionStorage.removeItem("access_token");
              window.location.href = "/";
              throw new Error("Unauthorized");
            }

            if (!response.ok) return [];

            const data = await response.json();
            return data.items || [];
          })
        );

        const results: RunResult[] = resultsResponses.flat();

        const latencyValues = results
          .filter(
            (result) =>
              result.status === "ok" &&
              Number.isFinite(Number(result.latency_ms))
          )
          .map((result) => Number(result.latency_ms));

        const avgLatency =
          latencyValues.length > 0
            ? latencyValues.reduce((sum, value) => sum + value, 0) /
              latencyValues.length
            : null;

        const qualityValues = results.flatMap((result) =>
          (result.judgments || [])
            .map((judgment) => Number(judgment.score))
            .filter((score) => Number.isFinite(score))
        );

        const avgQuality =
          qualityValues.length > 0
            ? qualityValues.reduce((sum, value) => sum + value, 0) /
              qualityValues.length
            : null;

        if (!cancelled) {
          setStats({
            totalRuns,
            totalCost,
            avgLatency,
            avgQuality,
          });
        }
      } catch (error) {
        console.error("Error fetching dashboard stats:", error);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchStats();

    return () => {
      cancelled = true;
    };
  }, []);

  const cards: StatCardProps[] = [
    {
      id: "total-runs",
      title: "Total Runs",
      value: loading ? "..." : stats.totalRuns,
      change: "+20%",
      changeType: "positive",
      icon: TrendingUp,
    },
    {
      id: "total-cost",
      title: "Total Cost",
      value: loading ? "..." : `$${stats.totalCost.toFixed(2)}`,
      change: "+15%",
      changeType: "negative",
      icon: CircleArrowOutUpLeft,
    },
    {
      id: "avg-latency",
      title: "Avg. Latency",
      value: loading
        ? "..."
        : stats.avgLatency !== null
          ? `${Math.round(stats.avgLatency).toLocaleString("en-US")}ms`
          : "—",
      change: "+32%",
      changeType: "negative",
      icon: CalendarDays,
    },
    {
      id: "avg-quality-score",
      title: "Avg. Quality Score",
      value: loading
        ? "..."
        : stats.avgQuality !== null
          ? `${stats.avgQuality.toFixed(1)}/100`
          : "—",
      change: "+12%",
      changeType: "positive",
      icon: Star,
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4 w-full min-[800px]:max-[956px]:grid-cols-2 max-[798px]:justify-items-center min-[800px]:max-[957px]:justify-items-center">
      {cards.map((card) => (
        <StatCard key={card.id} {...card} />
      ))}
    </div>
  );
}
