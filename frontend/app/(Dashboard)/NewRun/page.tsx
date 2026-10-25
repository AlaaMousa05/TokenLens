"use client";
import SideBar from "@/Components/SidBar/SideBar";

export default function NewRunPage() {
  return (
    <>
      <SideBar />
      <div className="mt-14 p-6 sm:ml-64">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-white">New Run</h1>
          <p className="text-sm text-slate-400">
            Configure your test, select models and run comparisons.
          </p>
        </div>
      </div>
    </>
  );
}