"use client";

import { useState } from "react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const hasInput = email.length > 0 || password.length > 0;

  return (
    <main className="mx-auto max-w-md px-6 py-16">
      <h1 className="text-3xl font-bold text-slate-900">Sign In</h1>
      <form className="mt-8 space-y-4" onSubmit={(e) => e.preventDefault()}>
        {/*
          BUG #5 (intentional): The validation error banner shows a generic
          "Error 001: Invalid input" message with NO field-level indicators &mdash;
          no red border, no `aria-invalid`, no helper text under the inputs. The user
          cannot tell which field is wrong or what the problem is. Do NOT fix this.
        */}
        {hasInput && (
          <div
            className="rounded bg-amber-50 px-4 py-3 text-sm text-amber-800"
            role="alert"
          >
            Error 001: Invalid input
          </div>
        )}

        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-slate-700"
          >
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm"
          />
        </div>

        <div>
          <label
            htmlFor="password"
            className="block text-sm font-medium text-slate-700"
          >
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm"
          />
        </div>

        <button
          type="submit"
          /* BUG #2 (intentional): `disabled` is hardcoded to `true` and never becomes
             enabled, even when both email and password are filled. The disabled state
             is not wired to form validation. Do NOT fix this. */
          disabled={true}
          className="w-full rounded-md bg-indigo-600 px-4 py-2 font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          Sign In
        </button>
      </form>
    </main>
  );
}
