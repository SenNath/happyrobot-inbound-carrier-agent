"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { LoadPerformancePoint } from "@/lib/api";

export function LoadPerformanceChart({ data }: { data: LoadPerformancePoint[] }) {
  return (
    <div className="h-[380px] w-full">
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="load_id" interval={0} angle={-16} textAnchor="end" height={80} />
          <YAxis yAxisId="percent" orientation="left" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
          <YAxis yAxisId="rate" orientation="right" tickFormatter={(v) => `$${v}`} />
          <Tooltip />
          <Legend />
          <Bar yAxisId="percent" dataKey="acceptance_rate" name="Acceptance %" fill="#0f6d92" radius={[6, 6, 0, 0]} />
          <Bar yAxisId="rate" dataKey="avg_offer" name="Avg Offer" fill="#1da9c3" radius={[6, 6, 0, 0]} />
          <Bar yAxisId="rate" dataKey="loadboard_rate" name="Loadboard Rate" fill="#74d1e3" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
