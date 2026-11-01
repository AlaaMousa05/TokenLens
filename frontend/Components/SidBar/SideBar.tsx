"use client";
import { CirclePlus, CpuAi, Database, LayoutDashboard, RotateCcwClock, Settings } from "lucide-react";
import Image from "next/image";
 
import { useState } from "react";
import Link from "next/link";

export default function SideBar() {
  // User dropdown state
  const [isOpen, setIsOpen] = useState(false);

  // Sidebar open/close state
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

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
                    TS
                  </span>
                  <span className="text-sm font-medium h-5 w-25">
                    Tharaa Sukaina
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
                    <p className="text-sm font-semibold">User</p>
                    <p className="truncate text-xs text-gray-400">
                      user@example.com
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
          <a href="https://flowbite.com/" className="flex items-center ps-2.5 mb-5">
            <Image
              src="https://flowbite.com/docs/images/logo.svg"
              className="h-6 me-3"
              width={24}
              height={24}
              unoptimized
              alt="Flowbite Logo"
            />
            <span className="self-center text-lg text-heading font-semibold whitespace-nowrap">
              LLM SandBox &<br /> Cost Profiler
            </span>
          </a>

          <ul className="space-y-2 font-medium">
            <li>
              <Link
                href="/dashboard"
                onClick={() => setIsSidebarOpen(false)}
                className="flex items-center px-2 py-1.5 text-body rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                <LayoutDashboard className="w-5 h-5 transition duration-75 group-hover:text-fg-brand " />
                <span className="ms-3">Dashboard</span>
              </Link>
            </li>

            <li>
              <Link
                href="/newrun"
                onClick={() => setIsSidebarOpen(false)}
                className="flex items-center px-2 py-1.5 text-body rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                <CirclePlus className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                <span className="flex-1 ms-3 whitespace-nowrap">New Run</span>
              </Link>
            </li>

            <li>
              <Link
                href="/datasets"
                onClick={() => setIsSidebarOpen(false)}
                className="flex items-center px-2 py-1.5 text-body rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                <Database className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                <span className="flex-1 ms-3 whitespace-nowrap">Data Sets</span>
              </Link>
            </li>

            <li>
              <Link
                href="/models"
                onClick={() => setIsSidebarOpen(false)}
                className="flex items-center px-2 py-1.5 text-body rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                <CpuAi className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                <span className="flex-1 ms-3 whitespace-nowrap">Models</span>
              </Link>
            </li>

            <li>
              <Link
                href="/runhistory"
                onClick={() => setIsSidebarOpen(false)}
                className="flex items-center px-2 py-1.5 text-body rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                <RotateCcwClock className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                <span className="flex-1 ms-3 whitespace-nowrap">Run History</span>
              </Link>
            </li>

            <li>
              <Link
                href="/settings"
                onClick={() => setIsSidebarOpen(false)}
                className="flex items-center px-2 py-1.5 text-body rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
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