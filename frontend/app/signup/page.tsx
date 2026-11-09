
"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  UserRound,
  Mail,
  LockKeyhole,
  Eye,
  EyeOff,
  Sparkles,
} from "lucide-react";

export default function SignupPage() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (loading) return;

    setError("");
    setSuccess("");

    // Check password confirmation
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/auth/register`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: name.trim(),
            email: email.trim(),
            password,
          }),
        }
      );

      // Read server response
      let data;

      try {
        data = await response.json();
      } catch {
        throw new Error("Invalid response from server. Please try again.");
      }

      // Handle backend errors
      if (!response.ok) {
        let errorMessage = "Registration failed. Please try again.";

        if (response.status === 409) {
          errorMessage = "This email is already registered.";
        } else if (typeof data.detail === "string") {
          errorMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          errorMessage = data.detail
            .map((item: { msg?: string }) => item.msg || "Invalid input")
            .join(", ");
        }

        throw new Error(errorMessage);
      }

      // Account created successfully
      setSuccess("Account created successfully! Redirecting to login...");

      setTimeout(() => {
        router.push("/");
      }, 1500);

    } catch (err) {
      if (err instanceof TypeError) {
        setError("Unable to connect to the server. Please try again.");
      } else {
        setError(
          err instanceof Error ? err.message : "Something went wrong."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const inputClass =
    "w-full h-12 rounded-lg bg-[#0b1024] border border-[#252c48] text-white pl-11 pr-4 text-sm outline-none focus:border-[#555af0] transition placeholder:text-gray-500";

  return (
    <main className="min-h-screen bg-[#060b1f] flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">

        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-7">
          <Sparkles className="text-[#777cff]" size={28} />
          <h1 className="text-2xl font-bold text-white">
            TokenLens
          </h1>
        </div>

        {/* Signup Card */}
        <div className="bg-[#11182d] border border-[#222b46] rounded-2xl p-8 shadow-2xl">

          <div className="text-center mb-7">
            <h2 className="text-2xl font-bold text-white mb-2">
              Create Account
            </h2>

            <p className="text-gray-400 text-sm">
              Sign up to start using TokenLens
            </p>
          </div>

          <form onSubmit={handleSignup} className="space-y-5">

            {/* Full Name */}
            <div>
              <label className="block text-sm text-gray-300 mb-2">
                Full Name
              </label>

              <div className="relative">
                <UserRound
                  size={18}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500"
                />

                <input
                  type="text"
                  placeholder="Enter your full name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className={inputClass}
                  required
                  maxLength={100}
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm text-gray-300 mb-2">
                Email Address
              </label>

              <div className="relative">
                <Mail
                  size={18}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500"
                />

                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={inputClass}
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm text-gray-300 mb-2">
                Password
              </label>

              <div className="relative">
                <LockKeyhole
                  size={18}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500"
                />

                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Create a password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={inputClass}
                  required
                  minLength={8}
                  maxLength={72}
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeOff size={18} />
                  ) : (
                    <Eye size={18} />
                  )}
                </button>
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm text-gray-300 mb-2">
                Confirm Password
              </label>

              <div className="relative">
                <LockKeyhole
                  size={18}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500"
                />

                <input
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={inputClass}
                  required
                  minLength={8}
                  maxLength={72}
                />

                <button
                  type="button"
                  onClick={() =>
                    setShowConfirmPassword(!showConfirmPassword)
                  }
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
                  aria-label={
                    showConfirmPassword
                      ? "Hide confirm password"
                      : "Show confirm password"
                  }
                >
                  {showConfirmPassword ? (
                    <EyeOff size={18} />
                  ) : (
                    <Eye size={18} />
                  )}
                </button>
              </div>
            </div>

            {/* Messages */}
            {error && (
              <p role="alert" className="text-red-500 text-sm">
                {error}
              </p>
            )}

            {success && (
              <p role="status" className="text-green-500 text-sm">
                {success}
              </p>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full h-12 rounded-lg bg-[#393dcc] hover:bg-[#555af0] disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition shadow-lg shadow-indigo-950/30"
            >
              {loading ? "Creating Account..." : "Create Account"}
            </button>

          </form>

          {/* Login Link */}
          <p className="text-center text-gray-400 text-sm mt-7">
            Already have an account?{" "}
            <Link
              href="/"
              className="text-[#8589ff] hover:text-white font-semibold transition"
            >
              Sign In
            </Link>
          </p>

        </div>

        <p className="text-center text-gray-600 text-xs mt-6">
          © 2026 TokenLens. All rights reserved.
        </p>

      </div>
    </main>
  );
}
