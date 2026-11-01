import React from "react";
import StatCard, { StatCardProps } from "../StatCard/StatCard";
import { TrendingUp, CalendarDays, CircleArrowOutUpLeft, Star } from "lucide-react";

const stats: StatCardProps[] = [
  {
    id: "total-Runs",
    title: "Total Runs",
    value: "12",
    change: "+20%",
    changeType: "positive",
    icon: TrendingUp,
  },
  {
    id: "total-cost",
    title: "Total Cost",
    value: "24.32$", 
     change: "+15%",
    changeType: "negative",
    icon: CircleArrowOutUpLeft,
    
  },
  {
    id: "avg-Latency",
    title: "Avg. Latency",
    value: "1,240ms",
     change: "+32%",
    changeType: "negative",
    icon: CalendarDays,  
  },
  {
    id: "avg-quality-score",
    title: "Avg. Quality Score",
    value: "78.6/100",
     change: "+12%",
    changeType: "positive",
    icon: Star,
  }
];

export default function StatsCards() {
  return (
   
<div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4 w-full min-[800px]:max-[956px]:grid-cols-2min-[800px]:max-[957px]:grid-cols-2 max-[798px]:justify-items-center
min-[800px]:max-[957px]:justify-items-center">      {stats.map((stat) => (
        <StatCard
          key={stat.id}
          {...stat}
        />
      ))}
    </div>
  );
}