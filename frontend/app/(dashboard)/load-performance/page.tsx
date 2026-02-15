import { LoadPerformanceChart } from "@/components/charts/load-performance-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { getLoadPerformance } from "@/lib/api";

export default async function LoadPerformancePage() {
  const data = await getLoadPerformance();
  const topDemandEquipment = data.reduce((best, row) => (row.total_calls > best.total_calls ? row : best), {
    equipment_type: "-",
    origin: "-",
    destination: "-",
    total_calls: 0,
    booked_calls: 0,
    booking_rate: 0,
    avg_final_rate: 0,
    avg_loadboard_rate: 0,
    avg_miles: 0,
    market_gap_pct: 0,
  });
  const bestBookingEquipment = data.reduce((best, row) => (row.booking_rate > best.booking_rate ? row : best), {
    equipment_type: "-",
    origin: "-",
    destination: "-",
    total_calls: 0,
    booked_calls: 0,
    booking_rate: 0,
    avg_final_rate: 0,
    avg_loadboard_rate: 0,
    avg_miles: 0,
    market_gap_pct: 0,
  });
  const averageGapPct = data.length > 0 ? data.reduce((sum, row) => sum + row.market_gap_pct, 0) / data.length : 0;

  const equipmentSummary = Array.from(
    data.reduce(
      (acc, row) => {
        const current = acc.get(row.equipment_type) ?? { calls: 0, booked: 0, marketGapWeighted: 0 };
        current.calls += row.total_calls;
        current.booked += row.booked_calls;
        current.marketGapWeighted += row.market_gap_pct * row.total_calls;
        acc.set(row.equipment_type, current);
        return acc;
      },
      new Map<string, { calls: number; booked: number; marketGapWeighted: number }>(),
    ),
  )
    .map(([equipment_type, value]) => ({
      equipment_type,
      calls: value.calls,
      booking_rate: value.calls > 0 ? (value.booked / value.calls) * 100 : 0,
      market_gap_pct: value.calls > 0 ? value.marketGapWeighted / value.calls : 0,
    }))
    .sort((a, b) => b.calls - a.calls);

  const topCorridors = [...data]
    .sort((a, b) => b.total_calls - a.total_calls)
    .slice(0, 5)
    .map((row) => ({
      corridor: `${row.origin} -> ${row.destination}`,
      booking_rate: row.booking_rate,
      avg_miles: row.avg_miles,
      calls: row.total_calls,
    }));

  const milesBands = [
    { label: "Short Haul (<=500 mi)", min: 0, max: 500 },
    { label: "Mid Haul (501-1000 mi)", min: 501, max: 1000 },
    { label: "Long Haul (>1000 mi)", min: 1001, max: Number.MAX_SAFE_INTEGER },
  ].map((band) => {
    const rows = data.filter((row) => row.avg_miles >= band.min && row.avg_miles <= band.max);
    const calls = rows.reduce((sum, row) => sum + row.total_calls, 0);
    const booked = rows.reduce((sum, row) => sum + row.booked_calls, 0);
    return { label: band.label, calls, booking_rate: calls > 0 ? (booked / calls) * 100 : 0 };
  });

  return (
    <>
      <header className="space-y-2">
        <Badge>Lane Efficiency</Badge>
        <h2 className="font-[var(--font-heading)] text-3xl font-semibold tracking-tight">Load Performance</h2>
      </header>
      <section className="grid gap-4 md:grid-cols-3">
        <Card className="bg-gradient-to-b from-card to-accent/20">
          <CardDescription>Equipment Types Tracked</CardDescription>
          <CardTitle className="mt-2 text-2xl">{data.length}</CardTitle>
          <p className="mt-2 text-xs text-muted-foreground">Types with at least one analyzed call</p>
        </Card>
        <Card className="bg-gradient-to-b from-card to-accent/20">
          <CardDescription>Highest Demand Segment</CardDescription>
          <CardTitle className="mt-2 text-2xl">{topDemandEquipment.equipment_type}</CardTitle>
          <p className="mt-2 text-xs text-muted-foreground">{topDemandEquipment.total_calls} calls analyzed</p>
        </Card>
        <Card className="bg-gradient-to-b from-card to-accent/20">
          <CardDescription>Best Booking Segment</CardDescription>
          <CardTitle className="mt-2 text-2xl">{bestBookingEquipment.equipment_type}</CardTitle>
          <p className="mt-2 text-xs text-muted-foreground">{bestBookingEquipment.booking_rate.toFixed(1)}% booking rate</p>
        </Card>
      </section>

      <Card>
        <CardTitle>Equipment Demand vs Pricing Efficiency</CardTitle>
        <CardDescription className="mt-1">
          Compare demand volume, booking conversion, and final-price vs loadboard gap by equipment type.
        </CardDescription>
        {equipmentSummary.length > 0 ? (
          <div className="mt-6">
            <LoadPerformanceChart data={equipmentSummary} />
            <p className="mt-4 text-xs text-muted-foreground">
              Average market gap across equipment types: {averageGapPct >= 0 ? "+" : ""}
              {averageGapPct.toFixed(1)}%
            </p>
          </div>
        ) : (
          <p className="mt-6 text-sm text-muted-foreground">No load performance metrics available yet.</p>
        )}
      </Card>

      {topCorridors.length > 0 ? (
        <Card>
          <CardTitle>Top Corridors (Origin to Destination)</CardTitle>
          <CardDescription className="mt-1">Most active lanes ranked by analyzed call volume.</CardDescription>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {topCorridors.map((row) => (
              <div key={row.corridor} className="rounded-lg border border-border/70 bg-card/80 p-3">
                <p className="text-sm font-medium">{row.corridor}</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  Calls: {row.calls} | Booking rate: {row.booking_rate.toFixed(1)}% | Avg miles: {row.avg_miles.toFixed(0)}
                </p>
              </div>
            ))}
          </div>
        </Card>
      ) : null}

      {milesBands.some((row) => row.calls > 0) ? (
        <section className="grid gap-4 md:grid-cols-3">
          {milesBands.map((row) => (
            <Card key={row.label} className="bg-gradient-to-b from-card to-accent/20">
              <CardDescription>{row.label}</CardDescription>
              <CardTitle className="mt-2 text-2xl">{row.booking_rate.toFixed(1)}%</CardTitle>
              <p className="mt-2 text-xs text-muted-foreground">{row.calls} calls in this band</p>
            </Card>
          ))}
        </section>
      ) : null}
    </>
  );
}
