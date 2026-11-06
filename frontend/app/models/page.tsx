"use client";
import SideBar from "@/Components/SidBar/SideBar";
import StatCard from "@/Components/StatCard/StatCard";
import { ArrowUpDown, Cpu, DollarSign, Edit2, Maximize2, MoreVertical, Plus, Search, Server, X } from "lucide-react";
import { useMemo, useState } from "react";
const panel = "rounded-xl border border-[#1b2750] bg-[#0b132b] p-5";
const field = "w-full rounded-lg border border-[#223062] bg-[#091129] px-3 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:border-[#4a5df0] focus:outline-none focus:ring-1 focus:ring-[#4a5df0]";

type ModelItem = {
  id: string;
  provider: "OpenAI" | "Anthropic" | "Meta" | "Google" | "Mistral";
  displayName: string;
  badge?: string;
  contextWindow: string;
  inputPricePerMtok: number;
  outputPricePerMtok: number;
  isActive: boolean;
};

// بيانات تجريبية
const initialModels: ModelItem[] = [
  { id: "1", provider: "OpenAI", displayName: "GPT-4o", badge: "Latest", contextWindow: "128K", inputPricePerMtok: 2.50, outputPricePerMtok: 10.00, isActive: true },
  { id: "2", provider: "OpenAI", displayName: "GPT-4o mini", contextWindow: "128K", inputPricePerMtok: 0.15, outputPricePerMtok: 0.60, isActive: true },
  { id: "3", provider: "OpenAI", displayName: "o1-mini", contextWindow: "128K", inputPricePerMtok: 1.10, outputPricePerMtok: 4.40, isActive: true },
  { id: "4", provider: "OpenAI", displayName: "o1-preview", contextWindow: "128K", inputPricePerMtok: 15.00, outputPricePerMtok: 60.00, isActive: false },
  { id: "5", provider: "Anthropic", displayName: "Claude 3.5 Sonnet", badge: "Latest", contextWindow: "200K", inputPricePerMtok: 3.00, outputPricePerMtok: 15.00, isActive: true },
  { id: "6", provider: "Anthropic", displayName: "Claude 3.5 Haiku", contextWindow: "200K", inputPricePerMtok: 0.80, outputPricePerMtok: 4.00, isActive: true },
  { id: "7", provider: "Anthropic", displayName: "Claude 3 Opus", contextWindow: "200K", inputPricePerMtok: 15.00, outputPricePerMtok: 75.00, isActive: false },
  { id: "8", provider: "Meta", displayName: "Llama 3.1 70B", contextWindow: "128K", inputPricePerMtok: 0.90, outputPricePerMtok: 0.90, isActive: true },
  { id: "9", provider: "Meta", displayName: "Llama 3.1 8B", contextWindow: "128K", inputPricePerMtok: 0.20, outputPricePerMtok: 0.20, isActive: true },
  { id: "10", provider: "Meta", displayName: "Llama 3 70B", contextWindow: "128K", inputPricePerMtok: 0.80, outputPricePerMtok: 0.80, isActive: true },
  { id: "11", provider: "Google", displayName: "Gemini 1.5 Pro", contextWindow: "2M", inputPricePerMtok: 12.50, outputPricePerMtok: 50.00, isActive: true },
  { id: "12", provider: "Google", displayName: "Gemini 1.5 Flash", contextWindow: "1M", inputPricePerMtok: 0.35, outputPricePerMtok: 1.50, isActive: true },
];

export default function ModelsPage() {
  const [models, setModels] = useState<ModelItem[]>(initialModels);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedProvider, setSelectedProvider] = useState("All Providers");
  const [selectedStatus, setSelectedStatus] = useState("All Statuses");
  
  // حالة نافذة إضافة/تعديل نموذج (Modal state) لصلاحيات الـ Admin
  const [isModalOpen, setIsModalOpen] = useState(false);

  // تبديل حالة النموذج (Active / Inactive)
  const toggleModelStatus = (id: string) => {
    setModels(prev => prev.map(m => m.id === id ? { ...m, isActive: !m.isActive } : m));
  };

  // تصفية النماذج حسب البحث ومزود الخدمة والحالة
  const filteredModels = useMemo(() => {
    return models.filter(m => {
      const matchesSearch = m.displayName.toLowerCase().includes(searchQuery.toLowerCase()) || 
                            m.provider.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesProvider = selectedProvider === "All Providers" || m.provider === selectedProvider;
      const matchesStatus = selectedStatus === "All Statuses" || 
                            (selectedStatus === "Active" && m.isActive) || 
                            (selectedStatus === "Inactive" && !m.isActive);
      return matchesSearch && matchesProvider && matchesStatus;
    });
  }, [models, searchQuery, selectedProvider, selectedStatus]);

  // إعداد بيانات البطاقات الإحصائية باستخدام مكون StatCard
  const modelStats = [
    {
      id: "total-providers",
      title: "Total Providers",
      value: "5",
      change: "OpenAI, Anthropic...",
      changeType: "positive" as const,
      icon: Server,
    },
    {
      id: "total-models",
      title: "Total Models",
      value: models.length,
      change: "Active & Inactive",
      changeType: "positive" as const,
      icon: Cpu,
    },
    {
      id: "max-context",
      title: "Max Context Window",
      value: "2M",
      change: "Gemini 1.5 Pro",
      changeType: "positive" as const,
      icon: Maximize2,
    },
    {
      id: "est-cost",
      title: "Estimated Monthly Cost",
      value: "$248.72",
      change: "1M in + 1M out",
      changeType: "positive" as const,
      icon: DollarSign,
    },
  ];

  return (
    <div className="min-h-screen bg-[#060b1f] text-slate-200">
      <SideBar />
      <main className="min-w-0 px-4 pb-8 pt-20 sm:ml-64 sm:px-8">        
        <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-white">Models</h1>
            <p className="mt-1 text-sm text-slate-400">
              Manage model providers, available models, and token pricing.
            </p>
          </div>
          
          {/* زر إضافة نموذج جديد */}
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 rounded-lg bg-[#3347e0] px-4 py-2.5 text-sm font-medium text-white hover:bg-[#4256f0] transition-colors"
          >
            <Plus size={16} />
            Add Model
          </button>
        </header>

        {/* شريط البحث والفلاتر */}
        <div className={`${panel} mb-6 flex flex-wrap items-center justify-between gap-4 py-4`}>
          <div className="relative flex-1 min-w-[280px]">
            <Search className="absolute left-3 top-3 text-slate-500" size={18} />
            <input
              type="text"
              placeholder="Search models..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`${field} pl-10`}
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* فلتر المزودين */}
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              className="rounded-lg border border-[#223062] bg-[#091129] px-3 py-2.5 text-sm text-slate-300 focus:border-[#4a5df0] focus:outline-none"
            >
              <option value="All Providers">All Providers</option>
              <option value="OpenAI">OpenAI</option>
              <option value="Anthropic">Anthropic</option>
              <option value="Meta">Meta</option>
              <option value="Google">Google</option>
            </select>

            {/* فلتر الحالة */}
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="rounded-lg border border-[#223062] bg-[#091129] px-3 py-2.5 text-sm text-slate-300 focus:border-[#4a5df0] focus:outline-none"
            >
              <option value="All Statuses">All Statuses</option>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
            </select>

            {/* زر الترتيب */}
            <button className="flex items-center gap-2 rounded-lg border border-[#223062] bg-[#091129] px-3 py-2.5 text-sm text-slate-300 hover:bg-white/5">
              <ArrowUpDown size={15} />
              Sort by: Name (A-Z)
            </button>
          </div>
        </div>

        {/* جدول عرض النماذج (Models Table) */}
        <section className={`${panel} mb-6 overflow-x-auto p-0`}>
          <table className="w-full text-left border-collapse min-w-[900px]">
            <thead>
              <tr className="border-b border-[#1b2750] text-xs font-medium text-slate-400 bg-[#091129]/50">
                <th className="py-3.5 px-4">Provider</th>
                <th className="py-3.5 px-4">Model Name</th>
                <th className="py-3.5 px-4">Context Window</th>
                <th className="py-3.5 px-4">Input / 1M Tokens</th>
                <th className="py-3.5 px-4">Output / 1M Tokens</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1b2750]/60 text-sm">
              {filteredModels.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    No models found matching your filters.
                  </td>
                </tr>
              ) : (
                filteredModels.map((model) => (
                  <tr key={model.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4 font-medium text-white flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full bg-blue-500"></span>
                      {model.provider}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2">
                        <span className="text-white font-medium">{model.displayName}</span>
                        {model.badge && (
                          <span className="rounded bg-emerald-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-500/20">
                            {model.badge}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">{model.contextWindow}</td>
                    <td className="py-3.5 px-4 text-slate-300">${model.inputPricePerMtok.toFixed(2)}</td>
                    <td className="py-3.5 px-4 text-slate-300">${model.outputPricePerMtok.toFixed(2)}</td>
                    <td className="py-3.5 px-4">
                      <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium border ${
                        model.isActive 
                          ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300" 
                          : "border-red-500/30 bg-red-500/10 text-red-300"
                      }`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${model.isActive ? "bg-emerald-400" : "bg-red-400"}`}></span>
                        {model.isActive ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-3">
                        <button className="text-slate-400 hover:text-white transition-colors" title="Edit Model">
                          <Edit2 size={16} />
                        </button>
                        {/* مفتاح التفعيل والإيقاف */}
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={model.isActive} 
                            onChange={() => toggleModelStatus(model.id)}
                            className="sr-only peer" 
                          />
                          <div className="w-9 h-5 bg-[#1b2750] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#3347e0]"></div>
                        </label>
                        <button className="text-slate-400 hover:text-white transition-colors">
                          <MoreVertical size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
          <div className="flex items-center justify-between border-t border-[#1b2750] px-4 py-3 text-xs text-slate-400">
            <span>Showing 1–{filteredModels.length} of {models.length} models</span>
            <div className="flex items-center gap-1">
              <button disabled className="rounded border border-[#223062] bg-[#091129] px-2.5 py-1 opacity-50 cursor-not-allowed">&lt;</button>
              <button className="rounded border border-[#4a5df0] bg-[#3347e0] px-3 py-1 text-white font-medium">1</button>
              <button disabled className="rounded border border-[#223062] bg-[#091129] px-2.5 py-1 opacity-50 cursor-not-allowed">&gt;</button>
            </div>
          </div>
        </section>
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 w-full">
          {modelStats.map((stat) => (
            <StatCard key={stat.id} {...stat} />
          ))}
        </div>

        {/* Modal إضافة جديد */}
        {isModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
            <div className={`${panel} w-full max-w-lg bg-[#0b132b] border-[#2a3a78]`}>
              <div className="flex items-center justify-between border-b border-[#1b2750] pb-3 mb-4">
                <h3 className="text-lg font-semibold text-white">Add New Model</h3>
                <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white">
                  <X size={20} />
                </button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="mb-1 block text-xs font-medium text-slate-300">Provider Name</label>
                  <input type="text" placeholder="e.g. OpenAI, Anthropic" className={field} />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-slate-300">Model Display Name</label>
                  <input type="text" placeholder="e.g. GPT-4o" className={field} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="mb-1 block text-xs font-medium text-slate-300">Input Price / 1M Tokens ($)</label>
                    <input type="number" step="0.01" placeholder="2.50" className={field} />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-medium text-slate-300">Output Price / 1M Tokens ($)</label>
                    <input type="number" step="0.01" placeholder="10.00" className={field} />
                  </div>
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-slate-300">Context Window</label>
                  <input type="text" placeholder="e.g. 128K, 200K" className={field} />
                </div>
              </div>
              <div className="mt-6 flex justify-end gap-3 border-t border-[#1b2750] pt-4">
                <button 
                  onClick={() => setIsModalOpen(false)}
                  className="rounded-lg border border-[#2a3a78] px-4 py-2 text-sm text-slate-300 hover:bg-white/5"
                >
                  Cancel
                </button>
                <button 
                  onClick={() => setIsModalOpen(false)}
                  className="rounded-lg bg-[#3347e0] px-5 py-2 text-sm font-medium text-white hover:bg-[#4256f0]"
                >
                  Save Model
                </button>
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}