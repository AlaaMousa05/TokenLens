
"use client";

import { useEffect, useState } from "react";
import {
  Database,
  Plus,
  Search,
  Eye,
  Edit,
  Trash2,
  Upload,
  FileText,
  X,
  Save,
} from "lucide-react";
import { base_usrl } from "@/lib/base-url";

// ================= Types =================

interface Dataset {
  id: string;
  name: string;
  description: string;
  source_format: string;
  is_golden: boolean;
  created_at: string;
  item_count: number;
}

interface DatasetListResponse {
  items: Dataset[];
  page: number;
  size: number;
  total: number;
}

interface DatasetItem {
  id: string;
  position: number;
  input: string;
  expected_output: string;
}

interface DatasetItemsResponse {
  items: DatasetItem[];
  page: number;
  size: number;
  total: number;
}

// ================= API Helper =================

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const apiUrl = base_usrl;

  const token =
    localStorage.getItem("access_token") ||
    sessionStorage.getItem("access_token");

  if (!token) {
    throw new Error("Authentication token not found. Please log in again.");
  }

  const headers = new Headers(options.headers);

  headers.set("Authorization", `Bearer ${token}`);

  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(
    `${apiUrl.replace(/\/$/, "")}${endpoint}`,
    {
      ...options,
      headers,
      cache: "no-store",
    }
  );

  if (!response.ok) {
    let errorMessage = `Request failed (${response.status})`;

    try {
      const errorData = await response.json();
      errorMessage =
        errorData.detail || errorData.message || errorMessage;
    } catch {
      // Server did not return JSON
    }

    throw new Error(errorMessage);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// ================= Main Component =================

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState(false);

  const [searchQuery, setSearchQuery] = useState("");

  // Toast
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  // Confirmation Dialog
  const [confirmDialog, setConfirmDialog] = useState<{
    message: string;
    onConfirm: () => void;
  } | null>(null);

  const showToast = (
    message: string,
    type: "success" | "error" = "success"
  ) => {
    setToast({ message, type });

    setTimeout(() => {
      setToast(null);
    }, 3000);
  };

  // Create Dataset
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newDatasetName, setNewDatasetName] = useState("");
  const [newDatasetDesc, setNewDatasetDesc] = useState("");
  const [activeTab, setActiveTab] = useState<"file" | "manual">("file");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const [manualInput, setManualInput] = useState("");
  const [manualExpectedOutput, setManualExpectedOutput] = useState("");

  // View Dataset
  const [selectedDataset, setSelectedDataset] =
    useState<Dataset | null>(null);

  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [datasetItems, setDatasetItems] = useState<DatasetItem[]>([]);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [itemsError, setItemsError] = useState("");

  // Edit Dataset
  const [editingDataset, setEditingDataset] =
    useState<Dataset | null>(null);

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [newIsGolden, setNewIsGolden] = useState(false);

  // Add / Edit Dataset Item
  const [isItemModalOpen, setIsItemModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<DatasetItem | null>(null);
  const [itemInput, setItemInput] = useState("");
  const [itemExpectedOutput, setItemExpectedOutput] = useState("");

  const filteredDatasets = datasets.filter((dataset) =>
    dataset.name.toLowerCase().includes(searchQuery.trim().toLowerCase())
  );

  // ================= GET /datasets =================

  const fetchDatasets = async () => {
    try {
      setIsLoading(true);
      setError("");

      const data = await apiRequest<DatasetListResponse>(
        "/datasets?page=1&size=20",
        { method: "GET" }
      );

      setDatasets(data.items);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load datasets."
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  // ================= GET Dataset Items =================

  const refreshDatasetItems = async (datasetId: string) => {
    const data = await apiRequest<DatasetItemsResponse>(
      `/datasets/${datasetId}/items?page=1&size=50`,
      { method: "GET" }
    );

    setDatasetItems(data.items);
  };

  // ================= View Dataset =================

  const handleViewDataset = async (dataset: Dataset) => {
    setSelectedDataset(dataset);
    setIsViewModalOpen(true);
    setDatasetItems([]);
    setItemsError("");

    try {
      setItemsLoading(true);

      const [datasetDetails, itemsResponse] = await Promise.all([
        apiRequest<Dataset>(
          `/datasets/${dataset.id}`,
          { method: "GET" }
        ),
        apiRequest<DatasetItemsResponse>(
          `/datasets/${dataset.id}/items?page=1&size=50`,
          { method: "GET" }
        ),
      ]);

      setSelectedDataset(datasetDetails);
      setDatasetItems(itemsResponse.items);
    } catch (err) {
      setItemsError(
        err instanceof Error
          ? err.message
          : "Failed to load dataset details."
      );
    } finally {
      setItemsLoading(false);
    }
  };

  // ================= Reset Create Form =================

  const resetCreateForm = () => {
    setNewDatasetName("");
    setNewDatasetDesc("");
    setUploadedFile(null);
    setManualInput("");
    setManualExpectedOutput("");
    setActiveTab("file");
  };

  // ================= POST /datasets/prompt =================

  const handleCreatePromptDataset = async () => {
    if (!newDatasetName.trim() || !manualInput.trim()) {
      showToast("Please enter the dataset name and input prompt.", "error");
      return;
    }

    try {
      setActionLoading(true);

      await apiRequest(
        "/datasets/prompt",
        {
          method: "POST",
          body: JSON.stringify({
            name: newDatasetName.trim(),
            description: newDatasetDesc.trim(),
            input: manualInput.trim(),
            expected_output: manualExpectedOutput.trim(),
          }),
        }
      );

      setIsCreateModalOpen(false);
      resetCreateForm();

      await fetchDatasets();

      showToast("Dataset created successfully.", "success");
    } catch (err) {
      showToast(
        err instanceof Error ? err.message : "Failed to create dataset.",
        "error"
      );
    } finally {
      setActionLoading(false);
    }
  };

  // ================= POST /datasets/upload =================

  const handleUploadDataset = async () => {
    if (!newDatasetName.trim() || !uploadedFile) {
      showToast("Please enter the dataset name and select a file.", "error");
      return;
    }

    try {
      setActionLoading(true);

      const formData = new FormData();

      formData.append("name", newDatasetName.trim());
      formData.append("description", newDatasetDesc.trim());
      formData.append("file", uploadedFile);

      await apiRequest(
        "/datasets/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      setIsCreateModalOpen(false);
      resetCreateForm();

      await fetchDatasets();

      showToast("Dataset uploaded successfully.", "success");
    } catch (err) {
      showToast(
        err instanceof Error ? err.message : "Failed to upload dataset.",
        "error"
      );
    } finally {
      setActionLoading(false);
    }
  };

  const handleCreateDataset = () => {
    if (activeTab === "file") {
      handleUploadDataset();
    } else {
      handleCreatePromptDataset();
    }
  };

  // ================= PATCH Dataset =================

  const handleUpdateDataset = async () => {
    if (!editingDataset || !newName.trim()) {
      showToast("Dataset name is required.", "error");
      return;
    }

    try {
      setActionLoading(true);

      await apiRequest(
        `/datasets/${editingDataset.id}`,
        {
          method: "PATCH",
          body: JSON.stringify({
            name: newName.trim(),
            description: newDescription.trim(),
            is_golden: newIsGolden,
          }),
        }
      );

      setIsEditModalOpen(false);
      setEditingDataset(null);

      await fetchDatasets();

      showToast("Dataset updated successfully.", "success");
    } catch (err) {
      showToast(
        err instanceof Error ? err.message : "Failed to update dataset.",
        "error"
      );
    } finally {
      setActionLoading(false);
    }
  };

  // ================= DELETE Dataset =================

  const handleDeleteDataset = (dataset: Dataset) => {
    setConfirmDialog({
      message: `Are you sure you want to delete "${dataset.name}"?`,
      onConfirm: async () => {
        setConfirmDialog(null);

        try {
          setActionLoading(true);

          await apiRequest(
            `/datasets/${dataset.id}`,
            { method: "DELETE" }
          );

          setDatasets((prev) =>
            prev.filter((item) => item.id !== dataset.id)
          );

          showToast("Dataset deleted successfully.", "success");
        } catch (err) {
          showToast(
            err instanceof Error ? err.message : "Failed to delete dataset.",
            "error"
          );
        } finally {
          setActionLoading(false);
        }
      },
    });
  };

  // ================= POST Dataset Item =================

  const handleCreateItem = async () => {
    if (!selectedDataset || !itemInput.trim()) {
      showToast("Input prompt is required.", "error");
      return;
    }

    try {
      setActionLoading(true);

      await apiRequest(
        `/datasets/${selectedDataset.id}/items`,
        {
          method: "POST",
          body: JSON.stringify({
            input: itemInput.trim(),
            expected_output: itemExpectedOutput.trim(),
          }),
        }
      );

      setIsItemModalOpen(false);
      resetItemForm();

      await refreshDatasetItems(selectedDataset.id);
      await fetchDatasets();

      showToast("Dataset item added successfully.", "success");
    } catch (err) {
      showToast(
        err instanceof Error ? err.message : "Failed to add item.",
        "error"
      );
    } finally {
      setActionLoading(false);
    }
  };

  // ================= PATCH Dataset Item =================

  const handleUpdateItem = async () => {
    if (!selectedDataset || !editingItem || !itemInput.trim()) {
      showToast("Input prompt is required.", "error");
      return;
    }

    try {
      setActionLoading(true);

      await apiRequest(
        `/datasets/${selectedDataset.id}/items/${editingItem.id}`,
        {
          method: "PATCH",
          body: JSON.stringify({
            input: itemInput.trim(),
            expected_output: itemExpectedOutput.trim(),
          }),
        }
      );

      setIsItemModalOpen(false);
      resetItemForm();

      await refreshDatasetItems(selectedDataset.id);
      await fetchDatasets();

      showToast("Dataset item updated successfully.", "success");
    } catch (err) {
      showToast(
        err instanceof Error ? err.message : "Failed to update item.",
        "error"
      );
    } finally {
      setActionLoading(false);
    }
  };

  // ================= DELETE Dataset Item =================

  const handleDeleteItem = (item: DatasetItem) => {
    if (!selectedDataset) return;

    const datasetId = selectedDataset.id;

    setConfirmDialog({
      message: "Are you sure you want to delete this item?",
      onConfirm: async () => {
        setConfirmDialog(null);

        try {
          setActionLoading(true);

          await apiRequest(
            `/datasets/${datasetId}/items/${item.id}`,
            { method: "DELETE" }
          );

          await refreshDatasetItems(datasetId);
          await fetchDatasets();

          showToast("Dataset item deleted successfully.", "success");
        } catch (err) {
          showToast(
            err instanceof Error ? err.message : "Failed to delete item.",
            "error"
          );
        } finally {
          setActionLoading(false);
        }
      },
    });
  };

  // ================= Reset Item Form =================

  const resetItemForm = () => {
    setItemInput("");
    setItemExpectedOutput("");
    setEditingItem(null);
  };

  const openAddItemModal = () => {
    resetItemForm();
    setIsItemModalOpen(true);
  };

  const openEditItemModal = (item: DatasetItem) => {
    setEditingItem(item);
    setItemInput(item.input);
    setItemExpectedOutput(item.expected_output);
    setIsItemModalOpen(true);
  };

  // ================= UI =================

  return (
    <div className="w-full min-h-screen bg-[#070b19] box-border pt-8 pb-12 pl-4 pr-4 min-[799px]:pl-72 min-[799px]:pr-8">
      <div className="w-full max-w-7xl mx-auto space-y-6">

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

          <button
            type="button"
            onClick={() => setIsCreateModalOpen(true)}
            className="inline-flex items-center justify-center gap-1.5 min-[799px]:gap-2 min-[799px]:mt-5 rounded-lg min-[799px]:rounded-xl bg-[#252fbb] w-1/2 mx-auto min-[799px]:w-50 min-[799px]:mx-0 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 transition-colors shadow-lg shadow-indigo-600/25 cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5 min-[799px]:w-5 min-[799px]:h-5" />
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
          <div className="w-full overflow-x-auto">
            <table className="w-full min-w-[720px] text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-800 text-xs font-semibold text-gray-400 uppercase tracking-wider bg-[#070b19]/50">
                  <th className="py-3 px-4">Name</th>
                  <th className="py-3 px-4">Rows</th>
                  <th className="py-3 px-4">Format</th>
                  <th className="py-3 px-4">Created At</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-gray-800 text-xs">
                {isLoading ? (
                  <tr>
                    <td colSpan={6} className="py-6 text-center text-gray-400">
                      Loading datasets...
                    </td>
                  </tr>
                ) : error ? (
                  <tr>
                    <td colSpan={6} className="py-6 text-center text-red-400">
                      {error}
                    </td>
                  </tr>
                ) : filteredDatasets.length > 0 ? (
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

                          <span className="truncate max-w-50">
                            {dataset.name}
                          </span>
                        </div>
                      </td>

                      <td className="py-3 px-4 text-gray-300">
                        {dataset.item_count}
                      </td>

                      <td className="py-3 px-4 text-gray-300 uppercase">
                        {dataset.source_format || "-"}
                      </td>

                      <td className="py-3 px-4 text-gray-400 text-[11px] whitespace-nowrap">
                         {dataset.created_at
  ? new Date(dataset.created_at).toLocaleString("en-US", {
      month: "2-digit",
      day: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
    })
  : "-"}
                      </td>

                      <td className="py-3 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium border ${
                            dataset.is_golden
                              ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                              : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                          }`}
                        >
                          {dataset.is_golden ? "Golden" : "Normal"}
                        </span>
                      </td>

                      <td className="py-3 px-4 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-1">
                          <button
                            type="button"
                            title="View"
                            onClick={() => handleViewDataset(dataset)}
                            className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                          >
                            <Eye className="w-4 h-4" />
                          </button>

                          <button
                            type="button"
                            title="Edit"
                            onClick={() => {
                              setEditingDataset(dataset);
                              setNewName(dataset.name);
                              setNewDescription(dataset.description || "");
                              setNewIsGolden(dataset.is_golden);
                              setIsEditModalOpen(true);
                            }}
                            className="p-1 rounded-lg text-gray-400 hover:text-indigo-400 hover:bg-gray-800 transition-colors"
                          >
                            <Edit className="w-4 h-4" />
                          </button>

                          <button
                            type="button"
                            title="Delete"
                            disabled={actionLoading}
                            onClick={() => handleDeleteDataset(dataset)}
                            className="p-1 rounded-lg text-gray-400 hover:text-red-400 hover:bg-gray-800 transition-colors disabled:opacity-50"
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

      {/* ================= Create Dataset Modal ================= */}

      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-2xl rounded-xl border border-slate-800 bg-[#0b132b] shadow-2xl text-slate-100 overflow-hidden flex flex-col max-h-[90vh]">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
              <h3 className="text-lg font-bold text-white">
                Create New Dataset
              </h3>

              <button
                type="button"
                onClick={() => {
                  setIsCreateModalOpen(false);
                  resetCreateForm();
                }}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

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
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Description
                </label>

                <input
                  type="text"
                  value={newDatasetDesc}
                  onChange={(e) => setNewDatasetDesc(e.target.value)}
                  placeholder="Brief summary of what this dataset tests..."
                  className="w-full px-3 py-2 text-sm rounded-lg border border-slate-800 bg-[#070b19] text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex border-b border-slate-800 pt-2 gap-4">
                <button
                  type="button"
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
                  type="button"
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

                    <p className="text-sm font-medium text-slate-300">
                      Drag and drop your dataset file here
                    </p>

                    <p className="text-xs text-slate-500 mt-1">
                      Supports .json or .csv files (max 10MB)
                    </p>

                    <input
                      type="file"
                      accept=".json,.csv"
                      className="hidden"
                      id="file-upload-input"
                      onChange={(e) =>
                        setUploadedFile(e.target.files?.[0] || null)
                      }
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
                        <span className="text-slate-200">
                          {uploadedFile.name}
                        </span>
                      </div>

                      <button
                        type="button"
                        onClick={() => setUploadedFile(null)}
                        className="text-slate-400 hover:text-red-400"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              )}

              {activeTab === "manual" && (
                <div className="space-y-3 p-3 rounded-lg bg-[#070b19] border border-slate-800 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">
                      Input Prompt (Question)
                    </label>

                    <textarea
                      rows={2}
                      value={manualInput}
                      onChange={(e) => setManualInput(e.target.value)}
                      placeholder="e.g. How to reset password?"
                      className="w-full p-2 bg-[#0b132b] border border-slate-800 rounded text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">
                      Expected Golden Output
                    </label>

                    <textarea
                      rows={2}
                      value={manualExpectedOutput}
                      onChange={(e) =>
                        setManualExpectedOutput(e.target.value)
                      }
                      placeholder="e.g. Click settings..."
                      className="w-full p-2 bg-[#0b132b] border border-slate-800 rounded text-white"
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-800 bg-[#070b19]">
              <button
                type="button"
                disabled={actionLoading}
                onClick={() => {
                  setIsCreateModalOpen(false);
                  resetCreateForm();
                }}
                className="bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-xl text-xs font-semibold text-gray-300 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>

              <button
                type="button"
                disabled={actionLoading}
                onClick={handleCreateDataset}
                className="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-xl text-xs font-semibold text-white transition-colors disabled:opacity-50"
              >
                {actionLoading ? "Creating..." : "Create Dataset"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= View Dataset Modal ================= */}

      {isViewModalOpen && selectedDataset && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-[#0b132b] border border-gray-800 rounded-2xl p-6 w-full max-w-3xl shadow-2xl text-white space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center border-b border-gray-800 pb-3">
              <div>
                <h3 className="text-lg font-bold">
                  Dataset Details: {selectedDataset.name}
                </h3>

                <p className="text-xs text-gray-400 mt-1">
                  {selectedDataset.description || "No description"}
                </p>
              </div>

              <button
                type="button"
                onClick={() => {
                  setIsViewModalOpen(false);
                  setIsItemModalOpen(false);
                }}
                className="text-gray-400 hover:text-white text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
              <div className="bg-[#070b19] border border-gray-800 rounded-lg p-3">
                <p className="text-gray-400">Rows</p>
                <p className="text-white font-semibold mt-1">
                  {selectedDataset.item_count}
                </p>
              </div>

              <div className="bg-[#070b19] border border-gray-800 rounded-lg p-3">
                <p className="text-gray-400">Format</p>
                <p className="text-white font-semibold mt-1 uppercase">
                  {selectedDataset.source_format || "-"}
                </p>
              </div>

              <div className="bg-[#070b19] border border-gray-800 rounded-lg p-3">
                <p className="text-gray-400">Type</p>
                <p
                  className={`font-semibold mt-1 ${
                    selectedDataset.is_golden
                      ? "text-amber-400"
                      : "text-emerald-400"
                  }`}
                >
                  {selectedDataset.is_golden ? "Golden" : "Normal"}
                </p>
              </div>
            </div>

            <div className="text-xs text-gray-400 break-all">
              <strong className="text-white">ID:</strong>{" "}
              {selectedDataset.id}
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-gray-800">
              <h4 className="text-sm font-semibold text-white">
                Dataset Items
              </h4>

              <button
                type="button"
                onClick={openAddItemModal}
                className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 px-3 py-2 text-xs font-semibold text-white"
              >
                <Plus className="w-4 h-4" />
                Add Item
              </button>
            </div>

            {itemsLoading ? (
              <p className="text-center text-gray-400 py-6 text-sm">
                Loading items...
              </p>
            ) : itemsError ? (
              <p className="text-center text-red-400 py-6 text-sm">
                {itemsError}
              </p>
            ) : datasetItems.length === 0 ? (
              <p className="text-center text-gray-500 py-6 text-sm">
                No items found in this dataset.
              </p>
            ) : (
              <div className="space-y-3">
                {datasetItems.map((item) => (
                  <div
                    key={item.id}
                    className="bg-[#070b19] border border-gray-800 rounded-xl p-4 space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-indigo-400">
                        Item #{item.position + 1}
                      </span>

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          title="Edit Item"
                          onClick={() => openEditItemModal(item)}
                          className="text-gray-400 hover:text-indigo-400"
                        >
                          <Edit className="w-4 h-4" />
                        </button>

                        <button
                          type="button"
                          title="Delete Item"
                          disabled={actionLoading}
                          onClick={() => handleDeleteItem(item)}
                          className="text-gray-400 hover:text-red-400 disabled:opacity-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <div>
                      <p className="text-[11px] text-gray-400 mb-1">
                        Input
                      </p>

                      <p className="text-sm text-gray-200 whitespace-pre-wrap break-words">
                        {item.input}
                      </p>
                    </div>

                    <div>
                      <p className="text-[11px] text-gray-400 mb-1">
                        Expected Output
                      </p>

                      <p className="text-sm text-gray-200 whitespace-pre-wrap break-words">
                        {item.expected_output || "-"}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="flex justify-end pt-3 border-t border-gray-800">
              <button
                type="button"
                onClick={() => setIsViewModalOpen(false)}
                className="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-xl text-sm font-semibold text-white transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= Add / Edit Item Modal ================= */}

      {isItemModalOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-[#0b132b] border border-gray-800 rounded-2xl p-6 w-full max-w-lg shadow-2xl text-white space-y-4">
            <div className="flex justify-between items-center border-b border-gray-800 pb-3">
              <h3 className="text-lg font-bold">
                {editingItem ? "Edit Dataset Item" : "Add Dataset Item"}
              </h3>

              <button
                type="button"
                onClick={() => {
                  setIsItemModalOpen(false);
                  resetItemForm();
                }}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div>
              <label className="block text-xs text-gray-400 mb-1">
                Input Prompt *
              </label>

              <textarea
                rows={4}
                value={itemInput}
                onChange={(e) => setItemInput(e.target.value)}
                placeholder="Enter input prompt..."
                className="w-full bg-[#070b19] border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs text-gray-400 mb-1">
                Expected Output
              </label>

              <textarea
                rows={4}
                value={itemExpectedOutput}
                onChange={(e) => setItemExpectedOutput(e.target.value)}
                placeholder="Enter expected output..."
                className="w-full bg-[#070b19] border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="flex justify-end gap-2 pt-3">
              <button
                type="button"
                disabled={actionLoading}
                onClick={() => {
                  setIsItemModalOpen(false);
                  resetItemForm();
                }}
                className="bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-xl text-sm font-semibold text-gray-300 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>

              <button
                type="button"
                disabled={actionLoading}
                onClick={editingItem ? handleUpdateItem : handleCreateItem}
                className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-xl text-sm font-semibold text-white transition-colors disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                {actionLoading
                  ? "Saving..."
                  : editingItem
                    ? "Save Changes"
                    : "Add Item"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= Edit Dataset Modal ================= */}

      {isEditModalOpen && editingDataset && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-[#0b132b] border border-gray-800 rounded-2xl p-6 w-full max-w-md shadow-2xl text-white space-y-4">
            <h3 className="text-lg font-bold border-b border-gray-800 pb-3">
              Edit Dataset
            </h3>

            <div>
              <label className="block text-xs text-gray-400 mb-1">
                Dataset Name
              </label>

              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="w-full bg-[#070b19] border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs text-gray-400 mb-1">
                Description
              </label>

              <textarea
                rows={3}
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                className="w-full bg-[#070b19] border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <label className="flex items-center gap-2 text-sm text-gray-300">
              <input
                type="checkbox"
                checked={newIsGolden}
                onChange={(e) => setNewIsGolden(e.target.checked)}
                className="accent-amber-500"
              />
              Golden Dataset
            </label>

            <div className="flex justify-end gap-2 pt-3">
              <button
                type="button"
                disabled={actionLoading}
                onClick={() => {
                  setIsEditModalOpen(false);
                  setEditingDataset(null);
                }}
                className="bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-xl text-sm font-semibold text-gray-300 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>

              <button
                type="button"
                disabled={actionLoading}
                onClick={handleUpdateDataset}
                className="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-xl text-sm font-semibold text-white transition-colors disabled:opacity-50"
              >
                {actionLoading ? "Saving..." : "Save Changes"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= Toast Notification ================= */}

      {toast && (
        <div
          className={`fixed top-6 right-6 z-[120] px-5 py-3 rounded-xl border shadow-2xl text-sm text-white ${
            toast.type === "success"
              ? "bg-[#111c35] border-emerald-500/40"
              : "bg-[#111c35] border-red-500/40"
          }`}
        >
          <div className="flex items-center gap-2">
            <span
              className={
                toast.type === "success"
                  ? "text-emerald-400"
                  : "text-red-400"
              }
            >
              {toast.type === "success" ? "✓" : "!"}
            </span>
            {toast.message}
          </div>
        </div>
      )}

      {/* ================= Confirmation Dialog ================= */}

      {confirmDialog && (
        <div className="fixed inset-0 z-110 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-sm rounded-2xl border border-gray-800 bg-[#0b132b] p-6 shadow-2xl">
            <h3 className="text-lg font-semibold text-white">
              Confirm Action
            </h3>

            <p className="mt-3 text-sm text-gray-400">
              {confirmDialog.message}
            </p>

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                disabled={actionLoading}
                onClick={() => setConfirmDialog(null)}
                className="rounded-lg bg-gray-800 px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 disabled:opacity-50"
              >
                Cancel
              </button>

              <button
                type="button"
                disabled={actionLoading}
                onClick={confirmDialog.onConfirm}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-500 disabled:opacity-50"
              >
                {actionLoading ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
