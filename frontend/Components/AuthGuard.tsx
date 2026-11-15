 
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { base_usrl } from "@/lib/base-url";

export default function AuthGuard({
  children,
}: {
  children: React.ReactNode;
}) {
  const API_URL = base_usrl;
  const router = useRouter();
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
        const response = await fetch(
          `${API_URL}/auth/me`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          localStorage.removeItem("access_token");
          sessionStorage.removeItem("access_token");
          localStorage.removeItem("role");
          sessionStorage.removeItem("role");
          router.replace("/");
          return;
        }

        setAuthorized(true);
      } catch {
        setAuthorized(false);
      }
    };

    verifyToken();
  }, [router, API_URL]);

  if (!authorized) {
    return (
      <div className="min-h-screen bg-[#060b1f] flex items-center justify-center text-white">
       Loading your workspace...
      </div>
    );
  }

  return <>{children}</>;
}
