import { FunnelInsightsChart } from "@/components/charts/funnel-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { getFunnel } from "@/lib/api";

export default async function FunnelPage() {
  const funnel = await getFunnel();
  const callsReceived = funnel.find((row) => row.stage === "Calls Received")?.value ?? funnel[0]?.value ?? 0;
  const verifiedCount = funnel.find((row) => row.stage === "Verified")?.value ?? 0;
  const loadsPitched = funnel.find((row) => row.stage === "Loads Pitched")?.value ?? 0;
  const bookedCount = funnel.find((row) => row.stage === "Booked")?.value ?? 0;

  const callRate = (value: number) => (callsReceived > 0 ? (value / callsReceived) * 100 : 0);
  const verifiedRate = (value: number) => (verifiedCount > 0 ? (value / verifiedCount) * 100 : 0);
  const pitchedRate = (value: number) => (loadsPitched > 0 ? (value / loadsPitched) * 100 : 0);

  return (
    <>
      <header className="space-y-2">
        <Badge>Pipeline Tracking</Badge>
        <h2 className="font-[var(--font-heading)] text-3xl font-semibold tracking-tight">Conversion Funnel</h2>
      </header>
      <Card>
        <CardTitle>Verification to Booking Progression</CardTitle>
        <CardDescription className="mt-1">
          Call-level conversion from received inbound calls to verified and booked outcomes.
        </CardDescription>
        {funnel.length > 0 ? (
          <div className="mt-6">
            <FunnelInsightsChart data={funnel} />
          </div>
        ) : (
          <p className="mt-6 text-sm text-muted-foreground">No funnel data available yet.</p>
        )}
      </Card>
      {funnel.length > 0 ? (
        <section className="grid gap-4 md:grid-cols-3">
          <Card className="bg-gradient-to-b from-card to-accent/20">
            <CardDescription>Verified Carriers</CardDescription>
            <CardTitle className="mt-2 text-2xl">{verifiedCount}</CardTitle>
            <p className="mt-2 text-xs text-muted-foreground">{callRate(verifiedCount).toFixed(1)}% of calls received</p>
          </Card>
          <Card className="bg-gradient-to-b from-card to-accent/20">
            <CardDescription>Total Booked</CardDescription>
            <CardTitle className="mt-2 text-2xl">{bookedCount}</CardTitle>
            <p className="mt-2 text-xs text-muted-foreground">{verifiedRate(bookedCount).toFixed(1)}% of verified calls</p>
          </Card>
          <Card className="bg-gradient-to-b from-card to-accent/20">
            <CardDescription>Successful Loads</CardDescription>
            <CardTitle className="mt-2 text-2xl">{bookedCount}</CardTitle>
            <p className="mt-2 text-xs text-muted-foreground">{pitchedRate(bookedCount).toFixed(1)}% of loads pitched</p>
          </Card>
        </section>
      ) : null}
    </>
  );
}
