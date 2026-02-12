import { DecisionChart } from "@/components/charts/decision-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { getNegotiations } from "@/lib/api";

export default async function NegotiationInsightsPage() {
  const insights = await getNegotiations();

  return (
    <>
      <header className="space-y-2">
        <Badge>Rate Strategy</Badge>
        <h2 className="font-[var(--font-heading)] text-3xl font-semibold tracking-tight">Negotiation Insights</h2>
      </header>

      <Card>
        <CardTitle>Decision Distribution</CardTitle>
        <CardDescription className="mt-1">Decision frequency and average round depth by outcome.</CardDescription>
        {insights.length > 0 ? (
          <div className="mt-6">
            <DecisionChart data={insights} />
          </div>
        ) : (
          <p className="mt-6 text-sm text-muted-foreground">No negotiation events logged yet.</p>
        )}
      </Card>

      <section className="grid gap-4 md:grid-cols-2">
        {insights.map((row) => (
          <Card key={row.decision}>
            <CardDescription>{row.decision}</CardDescription>
            <CardTitle className="mt-2 text-2xl">{row.count}</CardTitle>
            <p className="mt-2 text-xs text-muted-foreground">Average round: {row.avg_round.toFixed(2)}</p>
          </Card>
        ))}
      </section>
    </>
  );
}
