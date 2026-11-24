import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Log in" };

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6">
      <h1 className="text-2xl font-semibold tracking-tight">Log in</h1>
      <p className="mt-3 text-sm leading-6 text-stone-600">
        Workspace sign-in and the provider callback land on this route.
      </p>
      <Link href="/" className="mt-6 text-sm text-stone-900 underline">
        Back home
      </Link>
    </main>
  );
}
