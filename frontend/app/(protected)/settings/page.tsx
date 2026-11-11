"use client";

import SideBar from "@/Components/SidBar/SideBar";
import { ClipboardList, Database, Lock, Save, Sliders, User } from "lucide-react";
import React, { useEffect, useState } from "react";

const panelClass = "rounded-xl border border-[#1b2750] bg-[#0b132b] p-6 text-slate-200 shadow-lg";
const fieldClass = "w-full rounded-lg border border-[#223062] bg-[#091129] px-3.5 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:border-[#4a5df0] focus:outline-none focus:ring-1 focus:ring-[#4a5df0] transition-colors";
const labelClass = "mb-1.5 block text-xs font-medium text-slate-300";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function SettingsPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 1. Profile States
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);

  // 2. Run Defaults States
  const [temperature, setTemperature] = useState<number>(0.2);
  const [maxOutputTokens, setMaxOutputTokens] = useState<string>("1024");
  const [repeats, setRepeats] = useState<string>("1");
  const [defaultJudgeModel, setDefaultJudgeModel] = useState("Claude 3.5 Sonnet");

  // 3. Evaluation Preferences States
  const [defaultRubric, setDefaultRubric] = useState("General Response Quality");
  const [hideModelIdentities, setHideModelIdentities] = useState<boolean>(true);
  const [swapAnswerOrder, setSwapAnswerOrder] = useState<boolean>(true);

  // 4. Usage & Cost Controls States
  const [monthlySpendingCap, setMonthlySpendingCap] = useState<string>("50.00");
  const [currentMonthSpend, setCurrentMonthSpend] = useState<number>(0.0);

  // 5. Security States
  const [password, setPassword] = useState("••••••••");

  // جلب الإعدادات الحقيقية من الباك إند عند تحميل الصفحة
  useEffect(() => {
    async function fetchSettings() {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${API_URL}/settings`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });

        if (!res.ok) {
          throw new Error(res.status === 401 ? "Unauthorized. Please log in." : "Failed to load settings.");
        }

        const data = await res.json();
        // تعبئة البيانات القادمة حصرياً من الباك إند
        if (data.name) setName(data.name);
        if (data.email) setEmail(data.email);
        if (data.temperature !== undefined) setTemperature(data.temperature);
        if (data.maxOutputTokens) setMaxOutputTokens(String(data.maxOutputTokens));
        if (data.repeats) setRepeats(String(data.repeats));
        if (data.defaultJudgeModel) setDefaultJudgeModel(data.defaultJudgeModel);
        if (data.defaultRubric) setDefaultRubric(data.defaultRubric);
        if (data.hideModelIdentities !== undefined) setHideModelIdentities(data.hideModelIdentities);
        if (data.swapAnswerOrder !== undefined) setSwapAnswerOrder(data.swapAnswerOrder);
        if (data.monthlySpendingCap) setMonthlySpendingCap(String(data.monthlySpendingCap));
        if (data.currentMonthSpend !== undefined) setCurrentMonthSpend(data.currentMonthSpend);
      } catch (err) {
        console.error("Failed to fetch settings from backend:", err);
        setError(err instanceof Error ? err.message : "Failed to load settings.");
      } finally {
        setLoading(false);
      }
    }

    fetchSettings();
  }, []);

  // دالة تغيير الصورة الشخصية محلياً
  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const imageUrl = URL.createObjectURL(file);
      setAvatarUrl(imageUrl);
    }
  };

  // حفظ الإعدادات أو الملف الشخصي للباك إند مباشرة
  const handleSaveSettings = async (updatedData: object, successMessage: string) => {
    setSaving(true);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_URL}/settings`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(updatedData),
      });

      if (!res.ok) throw new Error("Failed to save settings.");

      alert(successMessage);
    } catch (err) {
      console.error(err);
      alert("Error saving settings to backend.");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveProfile = () => {
    handleSaveSettings({ name, email }, "Profile updated successfully!");
  };

  const handleChangePassword = async () => {
    if (password === "••••••••" || !password) {
      alert("Please enter a new valid password.");
      return;
    }
    await handleSaveSettings({ password }, "Password changed successfully!");
  };

  const handleSaveAllSettings = () => {
    handleSaveSettings(
      {
        temperature,
        maxOutputTokens: Number(maxOutputTokens),
        repeats: Number(repeats),
        defaultJudgeModel,
        defaultRubric,
        hideModelIdentities,
        swapAnswerOrder,
        monthlySpendingCap: Number(monthlySpendingCap),
      },
      "All settings saved successfully!"
    );
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#060b1f] text-white">
        <p className="animate-pulse text-sm text-slate-400">Loading settings...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#060b1f] text-slate-200 font-sans">
      <SideBar />

      <main className="min-w-0 px-4 pb-12 pt-20 sm:ml-64 sm:px-8">
        <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white">Settings</h1>
            <p className="mt-1 text-sm text-slate-400">
              Manage your account and default evaluation preferences.
            </p>
          </div>
        </header>

        {error && (
          <div className="mb-6 rounded-lg border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-400">
            {error}
          </div>
        )}

        {/* Settings Grid */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 mb-8">
          
          {/* 1. Profile Section */}
          <section className={panelClass}>
            <div className="flex items-start gap-4 mb-6">
              <div className="rounded-xl bg-blue-500/10 p-3 text-blue-400 border border-blue-500/20">
                <User size={22} />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Profile</h2>
                <p className="text-xs text-slate-400">Update your personal information.</p>
              </div>
            </div>

            {/* Avatar & Change Button */}
            <div className="flex items-center gap-5 mb-6">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#3347e0] text-xl font-bold text-white shadow-inner overflow-hidden border border-[#4a5df0]/40">
                {avatarUrl ? (
                  <img src={avatarUrl} alt="Avatar" className="h-full w-full object-cover" />
                ) : (
                  name.charAt(0) || "U"
                )}
              </div>
              <label className="cursor-pointer rounded-lg border border-[#2a3a78] bg-[#091129] px-4 py-2 text-xs font-medium text-slate-200 hover:bg-white/5 transition-colors">
                Change Avatar
                <input 
                  type="file" 
                  accept="image/*" 
                  className="hidden" 
                  onChange={handleAvatarChange} 
                />
              </label>
            </div>

            <div className="space-y-4">
              <div>
                <label className={labelClass}>Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className={fieldClass}
                />
              </div>

              <div>
                <label className={labelClass}>Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={fieldClass}
                />
              </div>

              <div className="pt-2">
                <button 
                  onClick={handleSaveProfile}
                  disabled={saving}
                  className="w-full rounded-lg bg-[#3347e0] py-2.5 text-sm font-medium text-white hover:bg-[#4256f0] transition-colors shadow-md disabled:opacity-50"
                >
                  {saving ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </div>
          </section>

          {/* 2. Run Defaults Section */}
          <section className={panelClass}>
            <div className="flex items-start gap-4 mb-6">
              <div className="rounded-xl bg-blue-500/10 p-3 text-blue-400 border border-blue-500/20">
                <Sliders size={22} />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Run Defaults</h2>
                <p className="text-xs text-slate-400">Set your preferred settings for new runs.</p>
              </div>
            </div>

            <div className="space-y-5">
              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <label className={labelClass}>Temperature</label>
                  <span className="rounded border border-[#223062] bg-[#091129] px-2 py-0.5 text-xs text-slate-200 font-mono">
                    {temperature}
                  </span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-full accent-[#3347e0] cursor-pointer bg-[#091129]"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>Max output tokens</label>
                  <select
                    value={maxOutputTokens}
                    onChange={(e) => setMaxOutputTokens(e.target.value)}
                    className={fieldClass}
                  >
                    <option value="512">512</option>
                    <option value="1024">1024</option>
                    <option value="2048">2048</option>
                    <option value="4096">4096</option>
                  </select>
                </div>

                <div>
                  <label className={labelClass}>Repeats</label>
                  <select
                    value={repeats}
                    onChange={(e) => setRepeats(e.target.value)}
                    className={fieldClass}
                  >
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                  </select>
                </div>
              </div>

              <div>
                <label className={labelClass}>Default Judge Model</label>
                <select
                  value={defaultJudgeModel}
                  onChange={(e) => setDefaultJudgeModel(e.target.value)}
                  className={fieldClass}
                >
                  <option value="Claude 3.5 Sonnet">Claude 3.5 Sonnet</option>
                  <option value="GPT-4o">GPT-4o</option>
                  <option value="Gemini 1.5 Pro">Gemini 1.5 Pro</option>
                </select>
              </div>
            </div>
          </section>

          {/* 3. Evaluation Preferences Section */}
          <section className={panelClass}>
            <div className="flex items-start gap-4 mb-6">
              <div className="rounded-xl bg-blue-500/10 p-3 text-blue-400 border border-blue-500/20">
                <ClipboardList size={22} />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Evaluation Preferences</h2>
                <p className="text-xs text-slate-400">Configure how your runs are evaluated.</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className={labelClass}>Default scoring rubric</label>
                <select
                  value={defaultRubric}
                  onChange={(e) => setDefaultRubric(e.target.value)}
                  className={fieldClass}
                >
                  <option value="General Response Quality">General Response Quality</option>
                  <option value="Code Generation & Accuracy">Code Generation & Accuracy</option>
                  <option value="Summarization Strictness">Summarization Strictness</option>
                </select>
              </div>

              <label className="flex items-center gap-3 cursor-pointer pt-2">
                <input
                  type="checkbox"
                  checked={hideModelIdentities}
                  onChange={(e) => setHideModelIdentities(e.target.checked)}
                  className="h-4 w-4 rounded border-[#223062] bg-[#091129] text-[#3347e0] focus:ring-[#4a5df0]"
                />
                <span className="text-sm text-slate-200">Hide model identities from judge</span>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={swapAnswerOrder}
                  onChange={(e) => setSwapAnswerOrder(e.target.checked)}
                  className="h-4 w-4 rounded border-[#223062] bg-[#091129] text-[#3347e0] focus:ring-[#4a5df0]"
                />
                <span className="text-sm text-slate-200">Swap answer order for judging</span>
              </label>
            </div>
          </section>

          {/* 4. Usage & Cost Controls Section */}
          <section className={panelClass}>
            <div className="flex items-start gap-4 mb-6">
              <div className="rounded-xl bg-blue-500/10 p-3 text-blue-400 border border-blue-500/20">
                <Database size={22} />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Usage & Cost Controls</h2>
                <p className="text-xs text-slate-400">Set a monthly spending cap to keep your costs under control.</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className={labelClass}>Monthly spending cap</label>
                <div className="relative">
                  <span className="absolute left-3.5 top-2.5 text-sm text-slate-400">$</span>
                  <input
                    type="text"
                    value={monthlySpendingCap}
                    onChange={(e) => setMonthlySpendingCap(e.target.value)}
                    className={`${fieldClass} pl-8`}
                  />
                </div>
              </div>

              <div className="pt-2">
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-slate-400">Current month spend</span>
                  <span className="font-medium text-slate-200">
                    ${currentMonthSpend.toFixed(2)} / ${monthlySpendingCap}
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-[#091129] border border-[#223062] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-[#3347e0] to-[#4a5df0]"
                    style={{
                      width: `${Math.min(100, (currentMonthSpend / parseFloat(monthlySpendingCap || "1")) * 100)}%`,
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </section>

          {/* 5. Security Section */}
          <section className={`${panelClass} lg:col-span-2`}>
            <div className="flex items-start gap-4 mb-6">
              <div className="rounded-xl bg-blue-500/10 p-3 text-blue-400 border border-blue-500/20">
                <Lock size={22} />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Security</h2>
                <p className="text-xs text-slate-400">Keep your account safe and secure.</p>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 items-end">
              <div>
                <label className={labelClass}>Password</label>
                <div className="flex gap-3">
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className={fieldClass}
                  />
                  <button 
                    onClick={handleChangePassword}
                    className="shrink-0 rounded-lg border border-[#2a3a78] bg-[#091129] px-4 py-2.5 text-xs font-medium text-slate-200 hover:bg-white/5 transition-colors"
                  >
                    Change Password
                  </button>
                </div>
              </div>

              <div className="rounded-lg border border-[#1b2750] bg-[#091129]/60 p-3.5">
                <p className="text-xs font-medium text-slate-400 mb-1">Session</p>
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span className="text-sm font-semibold text-emerald-400">JWT session active</span>
                </div>
              </div>
            </div>
          </section>
        </div>

        {/* Bottom Floating Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSaveAllSettings}
            disabled={saving}
            className="flex items-center gap-2 rounded-lg bg-[#3347e0] px-6 py-2.5 text-sm font-medium text-white hover:bg-[#4256f0] transition-colors shadow-lg shadow-blue-950/50 disabled:opacity-50"
          >
            <Save size={16} />
            {saving ? "Saving..." : "Save Settings"}
          </button>
        </div>
      </main>
    </div>
  );
}