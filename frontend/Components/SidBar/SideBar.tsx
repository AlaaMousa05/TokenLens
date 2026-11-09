"use client";
import {
  CirclePlus,
  CpuAi,
  Database,
  LayoutDashboard,
  RotateCcwClock,
  Settings,
  Sparkles,
} from "lucide-react";

import { useRouter } from "next/navigation";

import { useState, useEffect } from "react";
import Link from "next/link";
interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  created_at: string;
}
export default function SideBar() {
  // User dropdown state
  const [isOpen, setIsOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  // Sidebar open/close state
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const router = useRouter();
  const handleLogout = () => {
    localStorage.removeItem("access_token");
    sessionStorage.removeItem("access_token");

    setUser(null);
    setIsOpen(false);

    router.replace("/");
  };
  useEffect(() => {
    const fetchUser = async () => {
      const token =
        localStorage.getItem("access_token") ||
        sessionStorage.getItem("access_token");

      if (!token) return;

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/auth/me`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        );

        if (!response.ok) {
          throw new Error("Failed to fetch user data");
        }

        const data: User = await response.json();
        setUser(data);
      } catch (error) {
        console.error("Error fetching user:", error);
      }
    };

    fetchUser();
  }, []);

  const initials = user?.name
    ? user.name
        .trim()
        .split(/\s+/)
        .slice(0, 2)
        .map((part) => part[0])
        .join("")
        .toUpperCase()
    : "U";

  return (
    <>
      <nav className="fixed top-0 z-50 w-full bg-neutral-primary-soft">
        <div className="px-3 py-3 lg:px-5 lg:pl-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center justify-start rtl:justify-end">
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                aria-expanded={isSidebarOpen}
                aria-controls="top-bar-sidebar"
                aria-label="Toggle sidebar"
                type="button"
                className="sm:hidden flex items-center justify-center rounded-xl bg-[#1e293b] p-2 text-indigo-300 hover:bg-indigo-600 hover:text-white transition-colors"
              >
                <svg
                  className="w-5 h-5"
                  aria-hidden="true"
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeWidth="2"
                    d="M5 7h14M5 12h14M5 17h10"
                  />
                </svg>
              </button>

              <a href="https://flowbite.com" className="flex ms-2 md:me-24"></a>
            </div>

            <div className="flex items-center">
              <div className="relative">
                <button
                  onClick={() => setIsOpen(!isOpen)}
                  type="button"
                  className="flex items-center gap-3 px-3 py-2 text-white hover:bg-gray-900"
                  aria-label="User menu"
                >
                  <span className="flex h-4 w-7 items-center justify-center rounded-full bg-[#252fbb] font-semibold">
                    {initials}
                  </span>
                  <span className="text-sm font-medium h-5 w-25">
                    {user?.name || "Loading..."}
                  </span>
                  <span className="text-xs">▼</span>
                </button>

                <div
                  className={`${
                    isOpen ? "block" : "hidden"
                  } absolute right-0 top-full z-50 mt-2 w-56 rounded-lg border border-gray-700 bg-gray-900 p-2 text-white shadow-lg`}
                  id="dropdown-user"
                >
                  <div className="border-b border-gray-700 px-3 py-2">
                    <p className="text-sm font-semibold">
                      {user?.name || "Loading..."}
                    </p>
                    <p className="truncate text-xs text-gray-400">
                      {user?.email || ""}
                    </p>
                  </div>

                  <Link
                    href="/dashboard"
                    className="block rounded-md px-3 py-2 text-sm hover:bg-gray-800"
                  >
                    Dashboard
                  </Link>

                  <Link
                    href="/settings"
                    className="block rounded-md px-3 py-2 text-sm hover:bg-gray-800"
                  >
                    Settings
                  </Link>

                  <button
                    type="button"
                    onClick={handleLogout}
                    className="w-full rounded-md px-3 py-2 text-left text-sm hover:bg-gray-800"
                  >
                    Sign out
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <aside
        id="top-bar-sidebar"
        className={`fixed top-0 left-0 z-40 w-64 h-full transition-transform duration-300 ${
          isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        } sm:translate-x-0`}
        aria-label="Sidebar"
      >
        <div className="h-full px-3 py-4 overflow-y-auto bg-[#0b132b]">
          <a href="/dashboard" className="flex items-center ps-2.5 mb-5">
            <div className="w-10 h-10 rounded-xl bg-linear-to-br from-[#6255ed] to-[#3324a7] flex items-center justify-center me-3 shadow-lg shadow-purple-900/40">
              <Sparkles size={24} className="text-white" />
            </div>

            <span className="self-center text-lg text-white font-semibold whitespace-nowrap">
              LLM SandBox &<br /> Cost Profiler
            </span>
          </a>

          <ul className="space-y-2 font-medium">
            <li>
              <Link
                href="/dashboard"
                onClick={() => setIsSidebarOpen(false)}
                className="flex items-center px-2 py-1.5 text-white rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                <LayoutDashboard className="w-5 h-5 transition duration-75 group-hover:text-fg-brand " />
                <span className="ms-3">Dashboard</span>
              </Link>
            </li>

            <li>
              <Link
                href="/newrun"
                onClick={() => setIsSidebarOpen(false)}
                className="flex items-center px-2 py-1.5 text-white rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                <CirclePlus className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                <span className="flex-1 ms-3 whitespace-nowrap">New Run</span>
              </Link>
            </li>

            <li>
              <Link
                href="/datasets"
                onClick={() => setIsSidebarOpen(false)}
                className="flex items-center px-2 py-1.5 text-white rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                <Database className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                <span className="flex-1 ms-3 whitespace-nowrap">Data Sets</span>
              </Link>
            </li>

            <li>
              <Link
                href="/models"
                onClick={() => setIsSidebarOpen(false)}
                className="flex items-center px-2 py-1.5 text-white rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                <CpuAi className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                <span className="flex-1 ms-3 whitespace-nowrap">Models</span>
              </Link>
            </li>

            <li>
              <Link
                href="/runhistory"
                onClick={() => setIsSidebarOpen(false)}
                className="flex items-center px-2 py-1.5 text-white rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                <RotateCcwClock className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                <span className="flex-1 ms-3 whitespace-nowrap">
                  Run History
                </span>
              </Link>
            </li>

            <li>
              <Link
                href="/settings"
                onClick={() => setIsSidebarOpen(false)}
                className="flex items-center px-2 py-1.5 text-white rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                <Settings className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                <span className="flex-1 ms-3 whitespace-nowrap">Settings</span>
              </Link>
            </li>
          </ul>
        </div>
      </aside>
    </>
  );
}
