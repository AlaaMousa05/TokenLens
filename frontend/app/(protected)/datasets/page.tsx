"use client";

import { useState } from "react";
import { Database, Plus, Search, Eye, Edit, Trash2, Upload, FileText, X } from "lucide-react";

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

  // State الخاصة بنافذة إنشاء Dataset جديدة
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newDatasetName, setNewDatasetName] = useState("");
  const [newDatasetDesc, setNewDatasetDesc] = useState("");
  const [activeTab, setActiveTab] = useState<"file" | "manual">("file");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  // States الخاصة بنوافذ المعاينة والتعديل
  const [selectedDataset, setSelectedDataset] = useState<any>(null);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);

  const [editingDataset, setEditingDataset] = useState<any>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [newName, setNewName] = useState("");

  const filteredDatasets = datasets.filter((dataset) =>
    dataset.name.toLowerCase().includes(searchQuery.trim().toLowerCase())
  );

  // دالة إضافة Dataset جديدة للقائمة
  const handleCreateDataset = () => {
    if (!newDatasetName.trim()) return;
    
    const newEntry = {
      id: String(datasets.length + 1),
      name: newDatasetName,
      rows: uploadedFile ? 25 : 1, // رقم تقريبي افتراضي حسب الإدخال
      size: uploadedFile ? "54.2 KB" : "1.2 KB",
      createdAt: "Just now",
      tags: ["Custom"],
    };

    setDatasets([newEntry, ...datasets]);
    setIsCreateModalOpen(false);
    setNewDatasetName("");
    setNewDatasetDesc("");
    setUploadedFile(null);
  };

  return (
    <div className="pl-72 pr-8 pt-8 pb-12 w-full min-h-screen bg-[#070b19] box-border">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header Section */}
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

          {/* زر فتح نافذة إنشاء Dataset جديدة */}
          <button
            type="button"
            onClick={() => setIsCreateModalOpen(true)}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#252fbb] px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 transition-colors shadow-lg shadow-indigo-600/25 cursor-pointer"
          >
            <Plus className="w-5 h-5" />
            New Dataset
          </button>
        </div>

        {/* Search Bar */}
        <div className="flex items-center justify-between bg-[#0b132b] border border-gray-800/80 rounded-xl p-4 shadow-md">
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

        {/* Data Table */}
        <div className="w-full bg-[#0b132b] border border-gray-800/80 rounded-xl overflow-hidden shadow-xl">
          <div className="w-full">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-800 text-xs font-semibold text-gray-400 uppercase tracking-wider bg-[#070b19]/50">
                  <th className="py-3 px-4">Name</th>
                  <th className="py-3 px-4">Rows</th>
                  <th className="py-3 px-4">Size</th>
                  <th className="py-3 px-4">Created At</th>
                  <th className="py-3 px-4">Tags</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-gray-800 text-xs">
                {filteredDatasets.length > 0 ? (
                  filteredDatasets.map((dataset) => (
                    <tr
                      key={dataset.id}
                      className="hover:bg-gray-900/50 transition-colors"
                    >
                      <td className="py-3 px-4 font-medium text-white">
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-lg bg-indigo-600/20 flex items-center justify-center text-indigo-400 shrink-0">
                            <Database className="w-3.5 h-3.5" />
                          </div>
                          <span className="truncate max-w-50">{dataset.name}</span>
                        </div>
                      </td>

                      <td className="py-3 px-4 text-gray-300">{dataset.rows}</td>
                      <td className="py-3 px-4 text-gray-300">{dataset.size}</td>
                      <td className="py-3 px-4 text-gray-400 text-[11px] whitespace-nowrap">
                        {dataset.createdAt}
                      </td>

                      <td className="py-3 px-4">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {dataset.tags[0]}
                        </span>
                      </td>

                      <td className="py-3 px-4 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-1">
                          {/* زر المعاينة */}
                          <button
                            type="button"
                            title="View"
                            onClick={() => {
                              setSelectedDataset(dataset);
                              setIsViewModalOpen(true);
                            }}
                            className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                          >
                            <Eye className="w-4 h-4" />
                          </button>

                          {/* زر التعديل */}
                          <button
                            type="button"
                            title="Edit"
                            onClick={() => {
                              setEditingDataset(dataset);
                              setNewName(dataset.name);
                              setIsEditModalOpen(true);
                            }}
                            className="p-1 rounded-lg text-gray-400 hover:text-indigo-400 hover:bg-gray-800 transition-colors"
                          >
                            <Edit className="w-4 h-4" />
                          </button>

                          {/* زر الحذف */}
                          <button
                            type="button"
                            title="Delete"
                            onClick={() =>
                              setDatasets((prev) =>
                                prev.filter((d) => d.id !== dataset.id)
                              )
                            }
                            className="p-1 rounded-lg text-gray-400 hover:text-red-400 hover:bg-gray-800 transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="py-6 text-center text-gray-500">
                      No datasets found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>

      {/* ================= نافذة Create New Dataset (تظهر عند الضغط على الزر) ================= */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-2xl rounded-xl border border-slate-800 bg-[#0b132b] shadow-2xl text-slate-100 overflow-hidden flex flex-col max-h-[90vh]">
            
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
              <h3 className="text-lg font-bold text-white">Create New Dataset</h3>
              <button 
                onClick={() => setIsCreateModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Body */}
            <div className="p-6 space-y-4 overflow-y-auto flex-1">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Dataset Name <span className="text-indigo-400">*</span>
                </label>
                <input
                  type="text"
                  value={newDatasetName}
                  onChange={(e) => setNewDatasetName(e.target.value)}
                  placeholder="e.g., Customer Support Edge Cases v1"
                  className="w-full px-3 py-2 text-sm rounded-lg border border-slate-800 bg-[#070b19] text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Description</label>
                <input
                  type="text"
                  value={newDatasetDesc}
                  onChange={(e) => setNewDatasetDesc(e.target.value)}
                  placeholder="Brief summary of what this dataset tests..."
                  className="w-full px-3 py-2 text-sm rounded-lg border border-slate-800 bg-[#070b19] text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Tabs */}
              <div className="flex border-b border-slate-800 pt-2 gap-4">
                <button
                  onClick={() => setActiveTab("file")}
                  className={`pb-2 text-xs font-medium transition-all relative ${
                    activeTab === "file" 
                      ? "text-indigo-400 border-b-2 border-indigo-500 font-semibold" 
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  Upload File (JSON/CSV)
                </button>
                <button
                  onClick={() => setActiveTab("manual")}
                  className={`pb-2 text-xs font-medium transition-all relative ${
                    activeTab === "manual" 
                      ? "text-indigo-400 border-b-2 border-indigo-500 font-semibold" 
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  Manual Entries
                </button>
              </div>

              {activeTab === "file" && (
                <div className="space-y-3">
                  <div className="border-2 border-dashed border-slate-800 hover:border-indigo-500/50 rounded-xl p-6 text-center bg-[#070b19]/50 transition cursor-pointer">
                    <Upload className="w-8 h-8 mx-auto text-slate-500 mb-2" />
                    <p className="text-sm font-medium text-slate-300">Drag and drop your dataset file here</p>
                    <p className="text-xs text-slate-500 mt-1">Supports .json or .csv files (max 10MB)</p>
                    <input 
                      type="file" 
                      accept=".json,.csv"
                      className="hidden" 
                      id="file-upload-input"
                      onChange={(e) => setUploadedFile(e.target.files?.[0] || null)}
                    />
                    <label 
                      htmlFor="file-upload-input" 
                      className="mt-3 inline-block px-4 py-1.5 text-xs font-medium text-indigo-400 border border-indigo-500/30 rounded-lg hover:bg-indigo-500/10 cursor-pointer transition"
                    >
                      Browse Computer
                    </label>
                  </div>

                  {uploadedFile && (
                    <div className="flex items-center justify-between p-3 rounded-lg bg-[#070b19] border border-slate-800 text-xs">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-indigo-400" />
                        <span className="text-slate-200">{uploadedFile.name}</span>
                      </div>
                      <button onClick={() => setUploadedFile(null)} className="text-slate-400 hover:text-red-400">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              )}

              {activeTab === "manual" && (
                <div className="space-y-3 p-3 rounded-lg bg-[#070b19] border border-slate-800 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">Input Prompt (Question)</label>
                    <textarea rows={2} placeholder="e.g. How to reset password?" className="w-full p-2 bg-[#0b132b] border border-slate-800 rounded text-white" />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Expected Golden Output</label>
                    <textarea rows={2} placeholder="e.g. Click settings..." className="w-full p-2 bg-[#0b132b] border border-slate-800 rounded text-white" />
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-800 bg-[#070b19]">
              <button
                onClick={() => setIsCreateModalOpen(false)}
                className="bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-xl text-xs font-semibold text-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateDataset}
                className="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-xl text-xs font-semibold text-white transition-colors"
              >
                Create Dataset
              </button>
            </div>
          </div>
        </div>
      )}

      {/* نافذة العرض (View Modal) */}
      {isViewModalOpen && selectedDataset && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-[#0b132b] border border-gray-800 rounded-2xl p-6 w-full max-w-lg shadow-2xl text-white space-y-4">
            <div className="flex justify-between items-center border-b border-gray-800 pb-3">
              <h3 className="text-lg font-bold">Dataset Details: {selectedDataset.name}</h3>
              <button onClick={() => setIsViewModalOpen(false)} className="text-gray-400 hover:text-white text-lg font-bold">✕</button>
            </div>
            <div className="space-y-2 text-sm text-gray-300">
              <p>🆔 <strong className="text-white">ID:</strong> {selectedDataset.id}</p>
              <p>📊 <strong className="text-white">Rows:</strong> {selectedDataset.rows}</p>
              <p>💾 <strong className="text-white">Size:</strong> {selectedDataset.size}</p>
              <p>📅 <strong className="text-white">Created At:</strong> {selectedDataset.createdAt}</p>
              <p>🏷️ <strong className="text-white">Tags:</strong> {selectedDataset.tags.join(", ")}</p>
            </div>
            <div className="flex justify-end pt-3">
              <button onClick={() => setIsViewModalOpen(false)} className="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-xl text-sm font-semibold text-white transition-colors">
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* نافذة التعديل (Edit Modal) */}
      {isEditModalOpen && editingDataset && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-[#0b132b] border border-gray-800 rounded-2xl p-6 w-full max-w-md shadow-2xl text-white space-y-4">
            <h3 className="text-lg font-bold border-b border-gray-800 pb-3">Edit Dataset Name</h3>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Dataset Name</label>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="w-full bg-[#070b19] border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div className="flex justify-end gap-2 pt-3">
              <button onClick={() => setIsEditModalOpen(false)} className="bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-xl text-sm font-semibold text-gray-300 transition-colors">
                Cancel
              </button>
              <button
                onClick={() => {
                  setDatasets((prev) =>
                    prev.map((d) => (d.id === editingDataset.id ? { ...d, name: newName } : d))
                  );
                  setIsEditModalOpen(false);
                }}
                className="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-xl text-sm font-semibold text-white transition-colors"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}