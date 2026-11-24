import type { Metadata } from "next";

export const metadata: Metadata = { title: "Brain" };

export default function BrainPage() {
  return (
    <section>
      <h1 className="text-2xl font-semibold tracking-tight">Brain</h1>
      <p className="mt-3 max-w-xl text-sm leading-6 text-stone-600">
        ACL-aware search across the documents this user is allowed to see.
      </p>
    </section>
  );
}
