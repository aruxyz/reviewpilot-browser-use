import Link from "next/link";

export default function HomePage() {
  return (
    <main>
      {/*
        BUG #3 (intentional): The hero section uses `py-96` (384px) vertical padding on
        mobile, which pushes the "View Pricing Plans" CTA below the fold on viewports
        <= 390px. The CTA exists in the DOM but requires scrolling to reach. On desktop
        the padding shrinks to `py-16` so the CTA is visible. Do NOT fix this.
      */}
      <section className="bg-slate-50 py-96 md:py-16">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <h1 className="text-5xl font-bold tracking-tight text-slate-900">
            ReviewPilot
          </h1>
          <p className="mt-6 text-xl text-slate-600">
            AI-powered UX reviews for your deployed web apps.
          </p>
          <p className="mt-8 text-slate-600">
            ReviewPilot deploys an AI browser agent that navigates your app,
            interacts with forms, and reports broken UX &mdash; disabled buttons,
            overflow navbars, hidden CTAs, dead links, and unclear validation.
          </p>
          <p className="mt-6 text-slate-600">
            Trusted by 10,000+ developers. Free for open-source projects. Setup in
            under 5 minutes. No configuration required. Works with any framework.
          </p>
          <p className="mt-6 text-slate-600">
            Stop shipping broken UX. Let ReviewPilot catch the issues your users
            would have found &mdash; before they find them.
          </p>
          <p className="mt-6 text-slate-600">
            Join thousands of teams who ship with confidence. ReviewPilot runs on
            every PR, on every deploy, on every platform.
          </p>
          <div className="mt-12">
            <Link
              href="/pricing"
              className="inline-block rounded-lg bg-indigo-600 px-8 py-4 text-lg font-semibold text-white hover:bg-indigo-500"
            >
              View Pricing Plans
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
