import type { ReactNode } from "react";

import { SiteHeader } from "@/components/site-header";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto flex min-h-screen max-w-5xl flex-col px-6">
      <SiteHeader />
      <main className="flex-1 py-8">{children}</main>
    </div>
  );
}
