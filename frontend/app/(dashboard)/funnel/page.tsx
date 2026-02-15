import { FunnelInsightsChart } from "@/components/charts/funnel-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { getFunnel } from "@/lib/api";

export default async function FunnelPage() {
  const funnel = await getFunnel();
  const top = funnel[0]?.value ?? 0;
  const stageStats = funnel.map((row, idx) => {
    const previous = idx === 0 ? top : funnel[idx - 1]?.value ?? 0;
    const stageRate = previous > 0 ? (row.value / previous) * 100 : 0;
    return {
      ...row,
      stageRate,
      dropOff: Math.max(previous - row.value, 0),
    };
  });

  return (
    <>
      <header className="space-y-2">
        <Badge>Pipeline Tracking</Badge>
        <h2 className="font-[var(--font-heading)] text-3xl font-semibold tracking-tight">Conversion Funnel</h2>
      </header>
      <Card>
        <CardTitle>Verification to Booking Progression</CardTitle>
        <CardDescription className="mt-1">
          Stage counts and conversion rates from verified carriers to booked outcomes.
        </CardDescription>
        {funnel.length > 0 ? (
          <div className="mt-6">
            <FunnelInsightsChart data={funnel} />
          </div>
        ) : (
          <p className="mt-6 text-sm text-muted-foreground">No funnel data available yet.</p>
        )}
      </Card>
      {stageStats.length > 0 ? (
        <section className="grid gap-4 md:grid-cols-3">
          {stageStats.map((row) => (
            <Card key={row.stage} className="bg-gradient-to-b from-card to-accent/20">
              <CardDescription>{row.stage}</CardDescription>
              <CardTitle className="mt-2 text-2xl">{row.value}</CardTitle>
              <p className="mt-2 text-xs text-muted-foreground">
                Step conversion: {row.stageRate.toFixed(1)}% | Drop-off: {row.dropOff}
              </p>
            </Card>
          ))}
        </section>
      ) : null}
    </>
  );
}
