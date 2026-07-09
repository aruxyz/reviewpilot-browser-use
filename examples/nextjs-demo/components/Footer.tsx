import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white py-8">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-6 px-6 text-sm text-slate-600">
        <span>&copy; 2026 ReviewPilot</span>
        <Link href="/" className="hover:text-slate-900">
          Home
        </Link>
        <Link href="/pricing" className="hover:text-slate-900">
          Pricing
        </Link>
        <Link href="/login" className="hover:text-slate-900">
          Login
        </Link>
        {/*
          BUG #4 (intentional): These footer links point to `/nonexistent-page`, a route
          that does not exist. Clicking them returns a 404. Do NOT fix this.
        */}
        <Link href="/nonexistent-page" className="hover:text-slate-900">
          Privacy Policy
        </Link>
        <Link href="/nonexistent-page" className="hover:text-slate-900">
          Terms of Service
        </Link>
      </div>
    </footer>
  );
}
