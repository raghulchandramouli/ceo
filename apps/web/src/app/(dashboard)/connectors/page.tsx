import type { Metadata } from "next";

export const metadata: Metadata = { title: "Connectors" };

export default function ConnectorsPage() {
  return (
    <section>
      <h1 className="text-2xl font-semibold tracking-tight">Connectors</h1>
      <p className="mt-3 max-w-xl text-sm leading-6 text-stone-600">
        Install Slack and connect Google Workspace and Notion. Sync status shows up here.
      </p>
    </section>
  );
}
