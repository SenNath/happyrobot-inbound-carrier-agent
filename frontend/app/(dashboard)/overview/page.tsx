import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { getOverview } from "@/lib/api";

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(
    value,
  );
}

export default async function OverviewPage() {
  const overview = await getOverview();

  const cards = [
    { label: "Total Calls", value: overview.total_calls.toString(), help: "Inbound sessions tracked" },
    { label: "Verified Carriers", value: overview.verified_carriers.toString(), help: "FMCSA-qualified profiles" },
    { label: "Booked Loads", value: overview.booked_loads.toString(), help: "Negotiations finalized" },
    { label: "Accepted Revenue", value: formatCurrency(overview.revenue_accepted), help: "Total accepted offers" },
  ];

  return (
    <>
      <header className="space-y-2">
        <Badge>Live KPI View</Badge>
        <h2 className="font-[var(--font-heading)] text-3xl font-semibold tracking-tight">Overview KPIs</h2>
        <p className="max-w-2xl text-sm text-muted-foreground">
          Real-time operational visibility across carrier verification, conversion, sentiment, and accepted revenue.
        </p>
      </header>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => (
          <Card key={card.label}>
            <CardDescription>{card.label}</CardDescription>
            <CardTitle className="mt-3 text-3xl">{card.value}</CardTitle>
            <p className="mt-3 text-xs text-muted-foreground">{card.help}</p>
          </Card>
        ))}
      </section>

      <Card>
        <CardDescription>Average Sentiment</CardDescription>
        <CardTitle className="mt-3 text-4xl">{overview.avg_sentiment.toFixed(2)}</CardTitle>
        <p className="mt-3 text-sm text-muted-foreground">
          Scored from -1.00 (highly negative) to 1.00 (highly positive) from HappyRobot extract payloads.
        </p>
      </Card>
    </>
  );
}
