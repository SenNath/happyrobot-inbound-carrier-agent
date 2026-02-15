import { LoadPerformanceChart } from "@/components/charts/load-performance-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { getLoadPerformance } from "@/lib/api";

export default async function LoadPerformancePage() {
  const data = await getLoadPerformance();
  const topDemandEquipment = data.reduce((best, row) => (row.total_calls > best.total_calls ? row : best), {
    equipment_type: "-",
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
    total_calls: 0,
    booked_calls: 0,
    booking_rate: 0,
    avg_final_rate: 0,
    avg_loadboard_rate: 0,
    avg_miles: 0,
    market_gap_pct: 0,
  });
  const averageGapPct = data.length > 0 ? data.reduce((sum, row) => sum + row.market_gap_pct, 0) / data.length : 0;

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
        {data.length > 0 ? (
          <div className="mt-6">
            <LoadPerformanceChart data={data} />
            <p className="mt-4 text-xs text-muted-foreground">
              Average market gap across equipment types: {averageGapPct >= 0 ? "+" : ""}
              {averageGapPct.toFixed(1)}%
            </p>
          </div>
        ) : (
          <p className="mt-6 text-sm text-muted-foreground">No load performance metrics available yet.</p>
        )}
      </Card>
    </>
  );
}
