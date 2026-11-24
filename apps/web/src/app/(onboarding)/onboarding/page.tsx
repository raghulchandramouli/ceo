import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Set up" };

export default function OnboardingPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6">
      <h1 className="text-2xl font-semibold tracking-tight">Set up a workspace</h1>
      <p className="mt-3 text-sm leading-6 text-stone-600">
        Create the workspace, install the Slack app, and connect the first source.
      </p>
      <Link href="/connectors" className="mt-6 text-sm text-stone-900 underline">
        Go to connectors
      </Link>
    </main>
  );
}
