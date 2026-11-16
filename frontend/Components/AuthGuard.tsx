"use client";

import { base_usrl } from "@/lib/base-url";
import { usePathname, useRouter } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

function AuthGuardInner({ children }: { children: React.ReactNode }) {
  const API_URL = base_usrl;
  const router = useRouter();
  const pathname = usePathname();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    const verifyToken = async () => {
      const token =
        localStorage.getItem("access_token") ||
        sessionStorage.getItem("access_token");

      if (!token) {
        router.replace("/");
        return;
      }

      try {
        const response = await fetch(`${API_URL}/auth/me`, {
          method: "GET",
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          localStorage.removeItem("access_token");
          sessionStorage.removeItem("access_token");
          localStorage.removeItem("role");
          sessionStorage.removeItem("role");
          router.replace("/");
          return;
        }

        const user = await response.json();
        const isAdmin = String(user?.role ?? "").toLowerCase() === "admin";

        if (isAdmin && pathname === "/dashboard") {
          router.replace("/admin");
          return;
        }

        if (!isAdmin && pathname.startsWith("/admin")) {
          router.replace("/dashboard");
          return;
        }

        setAuthorized(true);
      } catch {
        setAuthorized(false);
      }
    };

    verifyToken();
  }, [router, API_URL, pathname]);

  if (!authorized) {
    return (
      <div className="min-h-screen bg-[#060b1f] flex items-center justify-center text-white">
        Loading your workspace...
      </div>
    );
  }

  return <>{children}</>;
}

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#060b1f] flex items-center justify-center text-white">
          Loading your workspace...
        </div>
      }
    >
      <AuthGuardInner>{children}</AuthGuardInner>
    </Suspense>
  );
}