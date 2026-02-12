import { FunnelInsightsChart } from "@/components/charts/funnel-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { getFunnel } from "@/lib/api";

export default async function FunnelPage() {
  const funnel = await getFunnel();

  return (
    <>
      <header className="space-y-2">
        <Badge>Pipeline Tracking</Badge>
        <h2 className="font-[var(--font-heading)] text-3xl font-semibold tracking-tight">Conversion Funnel</h2>
      </header>
      <Card>
        <CardTitle>Verification to Booking Progression</CardTitle>
        <CardDescription className="mt-1">How many calls reach each stage in the inbound sales flow.</CardDescription>
        {funnel.length > 0 ? (
          <div className="mt-6">
            <FunnelInsightsChart data={funnel} />
          </div>
        ) : (
          <p className="mt-6 text-sm text-muted-foreground">No funnel data available yet.</p>
        )}
      </Card>
    </>
  );
}
