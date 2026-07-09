import Link from "next/link";

export default function PricingPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="text-4xl font-bold text-slate-900">Pricing</h1>
      <p className="mt-4 text-slate-600">
        Simple, transparent pricing for every team.
      </p>

      <div className="mt-10 grid gap-6 md:grid-cols-3">
        <div className="rounded-lg border border-slate-200 p-6">
          <h2 className="text-xl font-semibold text-slate-900">Free</h2>
          <p className="mt-2 text-3xl font-bold text-slate-900">$0</p>
          <p className="mt-1 text-sm text-slate-500">per month</p>
          <ul className="mt-4 space-y-2 text-sm text-slate-600">
            <li>1 project</li>
            <li>50 reviews / month</li>
            <li>Community support</li>
          </ul>
        </div>

        <div className="rounded-lg border-2 border-indigo-600 p-6">
          <h2 className="text-xl font-semibold text-slate-900">Pro</h2>
          <p className="mt-2 text-3xl font-bold text-slate-900">$29</p>
          <p className="mt-1 text-sm text-slate-500">per month</p>
          <ul className="mt-4 space-y-2 text-sm text-slate-600">
            <li>10 projects</li>
            <li>Unlimited reviews</li>
            <li>Priority support</li>
          </ul>
          <Link
            href="/login"
            className="mt-6 inline-block rounded-md bg-indigo-600 px-4 py-2 font-semibold text-white hover:bg-indigo-500"
          >
            Get started
          </Link>
        </div>

        <div className="rounded-lg border border-slate-200 p-6">
          <h2 className="text-xl font-semibold text-slate-900">Enterprise</h2>
          <p className="mt-2 text-3xl font-bold text-slate-900">Custom</p>
          <p className="mt-1 text-sm text-slate-500">contact us</p>
          <ul className="mt-4 space-y-2 text-sm text-slate-600">
            <li>Unlimited projects</li>
            <li>SSO + SAML</li>
            <li>Dedicated support</li>
          </ul>
        </div>
      </div>
    </main>
  );
}
