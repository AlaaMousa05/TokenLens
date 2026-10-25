"use client";
import { CirclePlus, CpuAi, Database, LayoutDashboard, RotateCcwClock, Settings } from "lucide-react";

import { useState } from "react";

export default function SideBar() {
 const [isOpen, setIsOpen] = useState(false);
    return (
    <>
      <nav className="fixed top-0 z-50 w-full bg-neutral-primary-soft  ">
        <div className="px-3 py-3 lg:px-5 lg:pl-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center justify-start rtl:justify-end">
              <button
                data-drawer-target="top-bar-sidebar"
                data-drawer-toggle="top-bar-sidebar"
                aria-controls="top-bar-sidebar"
                type="button"
                className="sm:hidden text-heading bg-transparent box-border border border-transparent hover:bg-neutral-secondary-medium focus:ring-4 focus:ring-neutral-tertiary font-medium leading-5 rounded-base text-sm p-2 focus:outline-none"
              >
                <span className="sr-only">Open sidebar</span>
                <svg
                  className="w-6 h-6 bg-red-500"
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
              <a href="https://flowbite.com" className="flex ms-2 md:me-24">
                {/* <img src="https://flowbite.com/docs/images/logo.svg" className="h-6 me-3" alt="FlowBite Logo" /> */}
                {/* <span className="self-center text-lg font-semibold whitespace-nowrap dark:text-white">Flowbite</span> */}
              </a>
            </div>
            <div className="flex items-center">
  <div className="relative">
    <button
    onClick={() => setIsOpen(!isOpen)}
      type="button"
      className="flex items-center gap-3 rounded-lg border border-gray-700 px-3 py-2 text-white hover:bg-gray-800"
      aria-label="User menu"
    >
      <span className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-600 font-semibold">
        TS
      </span>
      <span className="text-sm font-medium">Tharaa Sukaina</span>
      <span className="text-xs">▼</span>
    </button>

    <div
className={`${isOpen ? "block" : "hidden"} absolute right-0 top-full z-50 mt-2 w-56 rounded-lg border border-gray-700 bg-gray-900 p-2 text-white shadow-lg`}      id="dropdown-user"
    >
      <div className="border-b border-gray-700 px-3 py-2">
        <p className="text-sm font-semibold">User</p>
        <p className="truncate text-xs text-gray-400">user@example.com</p>
      </div>

      <a
        href="/dashboard"
        className="block rounded-md px-3 py-2 text-sm hover:bg-gray-800"
      >
        Dashboard
      </a>
      <a
        href="/settings"
        className="block rounded-md px-3 py-2 text-sm hover:bg-gray-800"
      >
        Settings
      </a>
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
        className="fixed top-0 left-0 z-40 w-64 h-full transition-transform -translate-x-full sm:translate-x-0"
        aria-label="Sidebar"
      >
        <div className="h-full px-3 py-4 overflow-y-auto bg-neutral-primary-soft border-e border-default">
          <a
            href="https://flowbite.com/"
            className="flex items-center ps-2.5 mb-5"
          >
            <img
              src="https://flowbite.com/docs/images/logo.svg"
              className="h-6 me-3"
              alt="Flowbite Logo"
            />
            <span className="self-center text-lg text-heading font-semibold whitespace-nowrap">
              LLM SandBox &<br /> Cost Profiler
            </span>
          </a>
          <ul className="space-y-2 font-medium">
            <li>
              <a
                href="/"
                className="flex items-center px-2 py-1.5 text-body rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
              <LayoutDashboard className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                
                <span className="ms-3">Dashboard</span>
              </a>
            </li>
            <li>
              <a
                href="/NewRun"
                className="flex items-center px-2 py-1.5 text-body rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
               <CirclePlus className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />


                <span className="flex-1 ms-3 whitespace-nowrap">New Run</span>
              
              </a>
            </li>
            <li>
              <a
                href="#"
                className="flex items-center px-2 py-1.5 text-body rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                 <Database className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                <span className="flex-1 ms-3 whitespace-nowrap">Data Sets</span>
                 
              </a>
            </li>
            <li>
              <a
                href="#"
                className="flex items-center px-2 py-1.5 text-body rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                 <CpuAi className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                <span className="flex-1 ms-3 whitespace-nowrap">Models</span>
              </a>
            </li>
            <li>
              <a
                href="#"
                className="flex items-center px-2 py-1.5 text-body rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                 <RotateCcwClock className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                <span className="flex-1 ms-3 whitespace-nowrap">
                  Run History
                </span>
              </a>
            </li>
            <li>
              <a
                href="#"
                className="flex items-center px-2 py-1.5 text-body rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group"
              >
                <Settings className="w-5 h-5 transition duration-75 group-hover:text-fg-brand" />
                <span className="flex-1 ms-3 whitespace-nowrap">Settings</span>
              </a>
            </li>
          </ul>
        </div>
      </aside>

     {/* <div className="p-4 sm:ml-64 mt-14">
        <div className="p-4 border-1 border-default border-dashed rounded-base">
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="flex items-center justify-center h-24 rounded-base bg-neutral-secondary-soft">
              <p className="text-fg-disabled">
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
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 12h14m-7 7V5"
                  />
                </svg>
              </p>
            </div>
            <div className="flex items-center justify-center h-24 rounded-base bg-neutral-secondary-soft">
              <p className="text-fg-disabled">
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
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 12h14m-7 7V5"
                  />
                </svg>
              </p>
            </div>
            <div className="flex items-center justify-center h-24 rounded-base bg-neutral-secondary-soft">
              <p className="text-fg-disabled">
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
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 12h14m-7 7V5"
                  />
                </svg>
              </p>
            </div>
          </div>
          <div className="flex items-center justify-center h-48 rounded-base bg-neutral-secondary-soft mb-4">
            <p className="text-fg-disabled">
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
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 12h14m-7 7V5"
                />
              </svg>
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="flex items-center justify-center h-24 rounded-base bg-neutral-secondary-soft">
              <p className="text-fg-disabled">
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
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 12h14m-7 7V5"
                  />
                </svg>
              </p>
            </div>
            <div className="flex items-center justify-center h-24 rounded-base bg-neutral-secondary-soft">
              <p className="text-fg-disabled">
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
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 12h14m-7 7V5"
                  />
                </svg>
              </p>
            </div>
            <div className="flex items-center justify-center h-24 rounded-base bg-neutral-secondary-soft">
              <p className="text-fg-disabled">
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
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 12h14m-7 7V5"
                  />
                </svg>
              </p>
            </div>
            <div className="flex items-center justify-center h-24 rounded-base bg-neutral-secondary-soft">
              <p className="text-fg-disabled">
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
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 12h14m-7 7V5"
                  />
                </svg>
              </p>
            </div>
          </div>
          <div className="flex items-center justify-center h-48 rounded-base bg-neutral-secondary-soft mb-4">
            <p className="text-fg-disabled">
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
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 12h14m-7 7V5"
                />
              </svg>
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center justify-center h-24 rounded-base bg-neutral-secondary-soft">
              <p className="text-fg-disabled">
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
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 12h14m-7 7V5"
                  />
                </svg>
              </p>
            </div>
            <div className="flex items-center justify-center h-24 rounded-base bg-neutral-secondary-soft">
              <p className="text-fg-disabled">
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
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 12h14m-7 7V5"
                  />
                </svg>
              </p>
            </div>
            <div className="flex items-center justify-center h-24 rounded-base bg-neutral-secondary-soft">
              <p className="text-fg-disabled">
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
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 12h14m-7 7V5"
                  />
                </svg>
              </p>
            </div>
            <div className="flex items-center justify-center h-24 rounded-base bg-neutral-secondary-soft">
              <p className="text-fg-disabled">
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
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 12h14m-7 7V5"
                  />
                </svg>
              </p>
            </div>
          </div>
        </div>
      </div>*/}
    </>
  );
}
