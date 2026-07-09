import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="border-b border-slate-200 bg-white">
      {/*
        BUG #1 (intentional): The navbar uses a single flex row with `whitespace-nowrap`
        and NO responsive collapse (no hamburger menu, no flex-wrap, no overflow handling).
        On viewports <= 390px the links overflow horizontally — they get cut off and/or
        cause horizontal page scroll. Do NOT fix this.
      */}
      <div className="flex items-center gap-6 whitespace-nowrap px-6 py-4">
        <Link href="/" className="font-bold text-slate-900">
          ReviewPilot
        </Link>
        <Link href="/" className="text-slate-700 hover:text-slate-900">
          Home
        </Link>
        <Link href="/pricing" className="text-slate-700 hover:text-slate-900">
          Pricing
        </Link>
        <Link href="/login" className="text-slate-700 hover:text-slate-900">
          Login
        </Link>
        <Link href="/" className="text-slate-700 hover:text-slate-900">
          Docs
        </Link>
        <Link href="/" className="text-slate-700 hover:text-slate-900">
          About
        </Link>
        <Link href="/" className="text-slate-700 hover:text-slate-900">
          Contact
        </Link>
        <Link href="/" className="text-slate-700 hover:text-slate-900">
          Blog
        </Link>
      </div>
    </nav>
  );
}
