import { LoadPerformanceChart } from "@/components/charts/load-performance-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { getLoadPerformance } from "@/lib/api";

export default async function LoadPerformancePage() {
  const data = await getLoadPerformance();

  return (
    <>
      <header className="space-y-2">
        <Badge>Lane Efficiency</Badge>
        <h2 className="font-[var(--font-heading)] text-3xl font-semibold tracking-tight">Load Performance</h2>
      </header>

      <Card>
        <CardTitle>Offer vs Market Benchmark</CardTitle>
        <CardDescription className="mt-1">
          Compare acceptance rate, average offered price, and loadboard baseline per load.
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
