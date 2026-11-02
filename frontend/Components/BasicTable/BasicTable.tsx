import React from 'react';

const recentRunsData = [
  {
    id: 1,
    name: 'Marketing Copy Test',
    iconColor: 'bg-blue-600',
    models: 'GPT-4o, Claude 3.5',
    status: 'Completed',
    statusType: 'success',
    avgScore: '82.4',
    totalCost: '$3.12',
    createdAt: 'Apr 24, 2025 • 14:32',
  },
  {
    id: 2,
    name: 'Summarization Test',
    iconColor: 'bg-orange-600',
    models: 'GPT-4o, Llama 3.1',
    status: 'Completed',
    statusType: 'success',
    avgScore: '76.8',
    totalCost: '$2.47',
    createdAt: 'Apr 22, 2025 • 10:15',
  },
  {
    id: 3,
    name: 'Math Reasoning',
    iconColor: 'bg-amber-700',
    models: 'Claude 3.5, Gemini',
    status: 'Completed',
    statusType: 'success',
    avgScore: '71.3',
    totalCost: '$4.21',
    createdAt: 'Apr 20, 2025 • 16:45',
  },
  {
    id: 4,
    name: 'Code Generation',
    iconColor: 'bg-sky-600',
    models: 'GPT-4o, Llama 3.1',
    status: 'Failed',
    statusType: 'error',
    avgScore: '60.2',
    totalCost: '$1.80',
    createdAt: 'Apr 18, 2025 • 09:22',
  },
];

export default function RecentRunsTable() {
  return (
   
    <div className="w-full bg-[#0b132b] text-slate-300 p-6 rounded-xl border border-slate-800/80 font-sans shadow-xl">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-white">Recent Runs</h2>
        <button className="text-sm text-blue-400 hover:underline">
          View all
        </button>
      </div>

      {/* Table Container */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left border-collapse">
          <thead>
            <tr className="text-slate-400 border-b  border-slate-800/60 text-xs">
              <th scope="col" className="pb-3 font-normal">Name</th>
              <th scope="col" className="pb-3 font-normal">Models</th>
              <th scope="col" className="pb-3 font-normal">Status</th>
              <th scope="col" className="pb-3 font-normal">Avg. Score</th>
              <th scope="col" className="pb-3 font-normal">Total Cost</th>
              <th scope="col" className="pb-3 font-normal">Created At</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/40">
            {recentRunsData.map((row) => (
              <tr key={row.id} className="hover:bg-slate-800/20 transition-colors">
                <td className="py-4 pr-4 font-medium text-slate-200">
                  <div className="flex items-center gap-3">
                    <div className={`w-5 h-5 rounded flex items-center justify-center text-[10px] text-white font-bold ${row.iconColor}`}>
                      ||
                    </div>
                    <span>{row.name}</span>
                  </div>
                </td>
                <td className="py-4 px-2 text-slate-400">{row.models}</td>
                <td className="py-4 px-2">
                  {row.statusType === 'success' ? (
                    <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                      {row.status}
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-rose-950/60 text-rose-400 border border-rose-800/40">
                      ★ {row.status}
                    </span>
                  )}
                </td>
                <td className="py-4 px-2 text-slate-300 font-medium">{row.avgScore}</td>
                <td className="py-4 px-2 text-slate-300 font-medium">{row.totalCost}</td>
                <td className="py-4 px-2 text-slate-400 text-xs">{row.createdAt}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}