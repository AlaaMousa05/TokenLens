"use client";

import { useState } from "react";
import { Database, Plus, Search, Eye, Edit, Trash2 } from "lucide-react";

export default function DatasetsPage() {
  
  const [datasets, setDatasets] = useState([
    {
      id: "1",
      name: "Marketing Copy",
      rows: 12,
      size: "43.0 KB",
      createdAt: "Apr 24, 2025 • 14:32",
      tags: ["Normal"],
    },
    {
      id: "2",
      name: "Summarization Test",
      rows: 50,
      size: "210.0 KB",
      createdAt: "Apr 22, 2025 • 10:45",
      tags: ["Custom"],
    },
    {
      id: "3",
      name: "Math Prompts Evaluation",
      rows: 30,
      size: "130.40 KB",
      createdAt: "Apr 18, 2025 • 10:00",
      tags: ["Normal"],
    },
    {
      id: "4",
      name: "Communication",
      rows: 20,
      size: "64.00 KB",
      createdAt: "Apr 15, 2025 • 11:27",
      tags: ["Shared"],
    },
    {
      id: "5",
      name: "Code Generation",
      rows: 15,
      size: "89.50 KB",
      createdAt: "Apr 15, 2025 • 10:00",
      tags: ["Normal"],
    },
  ]);

  const [searchQuery, setSearchQuery] = useState("");

  // تصفية البيانات بناءً على البحث
  const filteredDatasets = datasets.filter((dataset) =>
    dataset.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="w-full min-w-0 space-y-6 md:pl-6 ">
      
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Database className="w-7 h-7 text-indigo-400" />
            Datasets
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Manage your datasets for testing and evaluation.
          </p>
        </div>

        <button
          type="button"
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 transition-colors shadow-lg shadow-indigo-600/20"
        >
          <Plus className="w-5 h-5" />
            New Dataset
        </button>
      </div>

      
      <div className="flex items-center justify-between bg-[#0b132b] border border-gray-800 rounded-xl p-4">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search datasets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#070b19] border border-gray-800 rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      
      <div className="w-full min-w-0 bg-[#0b132b] border border-gray-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-800 text-xs font-semibold text-gray-400 uppercase tracking-wider bg-[#070b19]/50">
                <th className="py-4 px-6">Name</th>
                <th className="py-4 px-6">Rows</th>
                <th className="py-4 px-6">Size</th>
                <th className="py-4 px-6">Created At</th>
                <th className="py-4 px-6">Tags</th>
                <th className="py-4 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800 text-sm">
              {filteredDatasets.length > 0 ? (
                filteredDatasets.map((dataset) => (
                  <tr
                    key={dataset.id}
                    className="hover:bg-gray-900/50 transition-colors"
                  >
                    <td className="py-4 px-6 font-medium text-white flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-indigo-600/20 flex items-center justify-center text-indigo-400">
                        <Database className="w-4 h-4" />
                      </div>
                      {dataset.name}
                    </td>
                    <td className="py-4 px-6 text-gray-300">{dataset.rows}</td>
                    <td className="py-4 px-6 text-gray-300">{dataset.size}</td>
                    <td className="py-4 px-6 text-gray-400 text-xs">
                      {dataset.createdAt}
                    </td>
                    <td className="py-4 px-6">
                      <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {dataset.tags[0]}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-right space-x-2">
                      <button
                        title="View"
                        className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        title="Edit"
                        className="p-1.5 rounded-lg text-gray-400 hover:text-indigo-400 hover:bg-gray-800 transition-colors"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        title="Delete"
                        onClick={() =>
                          setDatasets(
                            datasets.filter((d) => d.id !== dataset.id)
                          )
                        }
                        className="p-1.5 rounded-lg text-gray-400 hover:text-red-400 hover:bg-gray-800 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-gray-500">
                    No datasets found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}