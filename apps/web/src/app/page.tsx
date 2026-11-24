import Link from "next/link";

import { SiteHeader } from "@/components/site-header";

export default function HomePage() {
  return (
    <div className="mx-auto flex min-h-screen max-w-5xl flex-col px-6">
      <SiteHeader />
      <main className="flex-1 py-10">
        <h1 className="text-2xl font-semibold tracking-tight">Control plane</h1>
        <p className="mt-3 max-w-xl text-sm leading-6 text-stone-600">
          Sign in, connect Slack, Drive, and Notion, and search the company brain with the same
          permissions as the person asking.
        </p>
        <div className="mt-6 flex gap-4 text-sm">
          <Link href="/login" className="text-stone-900 underline">
            Log in
          </Link>
          <Link href="/onboarding" className="text-stone-900 underline">
            Set up a workspace
          </Link>
        </div>
      </main>
    </div>
  );
}
