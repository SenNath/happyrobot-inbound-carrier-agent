"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Gauge, HandCoins, Smile, Truck } from "lucide-react";

import { cn } from "@/lib/utils";

const navItems = [
  { href: "/overview", label: "Overview KPIs", icon: Gauge },
  { href: "/funnel", label: "Conversion Funnel", icon: BarChart3 },
  { href: "/negotiation-insights", label: "Negotiation Insights", icon: HandCoins },
  { href: "/sentiment-analytics", label: "Sentiment Analytics", icon: Smile },
  { href: "/load-performance", label: "Load Performance", icon: Truck },
];

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="mx-auto grid min-h-screen w-full max-w-[1300px] grid-cols-1 gap-8 px-4 pb-16 pt-10 lg:grid-cols-[260px_1fr] lg:px-8">
      <aside className="rounded-xl border border-border/60 bg-card/75 p-4 shadow-soft backdrop-blur lg:sticky lg:top-8 lg:h-[calc(100vh-4rem)]">
        <div className="mb-6 border-b border-border/70 pb-4">
          <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">HappyRobot</p>
          <h1 className="mt-2 text-xl font-semibold tracking-tight">Carrier Sales Console</h1>
        </div>
        <nav className="space-y-2">
          {navItems.map((item) => {
            const active = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition",
                  active ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted/70 hover:text-foreground",
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>

      <main className="space-y-8">{children}</main>
    </div>
  );
}
