"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { LoadPerformancePoint } from "@/lib/api";

export function LoadPerformanceChart({ data }: { data: LoadPerformancePoint[] }) {
  return (
    <div className="h-[380px] w-full">
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="equipment_type" />
          <YAxis yAxisId="percent" orientation="left" tickFormatter={(v) => `${v}%`} />
          <YAxis yAxisId="count" orientation="right" />
          <Tooltip />
          <Legend />
          <Bar yAxisId="percent" dataKey="booking_rate" name="Booking Rate %" fill="#0f6d92" radius={[6, 6, 0, 0]} />
          <Bar yAxisId="percent" dataKey="market_gap_pct" name="Final vs Market Gap %" fill="#1da9c3" radius={[6, 6, 0, 0]} />
          <Bar yAxisId="count" dataKey="total_calls" name="Calls" fill="#74d1e3" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
