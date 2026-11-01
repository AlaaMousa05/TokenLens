import React from "react";
export interface StatCardProps {
  id: string;
  title: string;
  value: number | string;

  change?: string;
  changeType?: "positive" | "negative";
  icon: React.ElementType;
  chartType?: string;
}

export default function StatCard({
  title,
  value,
  
  change,
  changeType,
  icon: Icon,
}: StatCardProps) {
  
  const color =
  changeType === "positive"
    ? "text-green-500"
    : "text-red-500";
  return (
    <div className="rounded-xl border border-gray-800 bg-[#0b132b] p-4 w-45 min-h-20">
      {/* Card Header */}
      <div className="mb-2 flex items-center justify-between ">
        <h3 className="text-sm text-r-400">{title}</h3>

        <div className="rounded-lg bg-gray-800 p-1">
          <Icon size={20} className="text-gray-300" />
        </div>
      </div>

      {/* Card Value */}
      <div className="text-xl font-semibold mb-2 text-white">{value}</div>

      {/* Card Footer */}
      <div className="mt-2 flex items-center justify-between">
        {/* <span className="text-xsm text-gray-400">{subText}</span> */}
       
        {/* Change */}
        {change && (
          <span className={"text-sm font-medium " + color}>{change}</span>
        )}

       
       
         
      </div>
    </div>
  );
}
