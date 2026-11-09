 
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function AuthGuard({
  children,
}: {
  children: React.ReactNode;
}) {
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
          `${process.env.NEXT_PUBLIC_API_URL}/auth/me`,
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
          router.replace("/");
          return;
        }

        setAuthorized(true);
      } catch {
        setAuthorized(false);
      }
    };

    verifyToken();
  }, [router]);

  if (!authorized) {
    return (
      <div className="min-h-screen bg-[#060b1f] flex items-center justify-center text-white">
        Checking authentication...
      </div>
    );
  }

  return <>{children}</>;
}
