import { LoadPerformanceChart } from "@/components/charts/load-performance-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { getLoadPerformance } from "@/lib/api";

export default async function LoadPerformancePage() {
  const data = await getLoadPerformance();
  const bestLane = data.reduce((best, row) => (row.acceptance_rate > best.acceptance_rate ? row : best), {
    load_id: "-",
    acceptance_rate: 0,
    avg_offer: 0,
    loadboard_rate: 0,
  });
  const averageGap =
    data.length > 0 ? data.reduce((sum, row) => sum + (row.avg_offer - row.loadboard_rate), 0) / data.length : 0;

  return (
    <>
      <header className="space-y-2">
        <Badge>Lane Efficiency</Badge>
        <h2 className="font-[var(--font-heading)] text-3xl font-semibold tracking-tight">Load Performance</h2>
      </header>
      <section className="grid gap-4 md:grid-cols-3">
        <Card className="bg-gradient-to-b from-card to-accent/20">
          <CardDescription>Lanes Tracked</CardDescription>
          <CardTitle className="mt-2 text-2xl">{data.length}</CardTitle>
          <p className="mt-2 text-xs text-muted-foreground">Loads with at least one negotiation event</p>
        </Card>
        <Card className="bg-gradient-to-b from-card to-accent/20">
          <CardDescription>Best Acceptance Lane</CardDescription>
          <CardTitle className="mt-2 text-2xl">{bestLane.load_id}</CardTitle>
          <p className="mt-2 text-xs text-muted-foreground">{bestLane.acceptance_rate.toFixed(1)}% acceptance rate</p>
        </Card>
        <Card className="bg-gradient-to-b from-card to-accent/20">
          <CardDescription>Avg Offer vs Market Gap</CardDescription>
          <CardTitle className="mt-2 text-2xl">{averageGap >= 0 ? "+" : ""}${averageGap.toFixed(0)}</CardTitle>
          <p className="mt-2 text-xs text-muted-foreground">Average offer minus loadboard baseline</p>
        </Card>
      </section>

      <Card>
        <CardTitle>Offer vs Market Benchmark</CardTitle>
        <CardDescription className="mt-1">
          Compare lane acceptance percentage against average offer and loadboard baseline to spot pricing opportunities.
        </CardDescription>
        {data.length > 0 ? (
          <div className="mt-6">
            <LoadPerformanceChart data={data} />
          </div>
        ) : (
          <p className="mt-6 text-sm text-muted-foreground">No load performance metrics available yet.</p>
        )}
      </Card>
    </>
  );
}
