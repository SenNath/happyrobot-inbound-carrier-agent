"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type EquipmentInsight = {
  equipment_type: string;
  booking_rate: number;
  market_gap_pct: number;
  calls: number;
};

export function LoadPerformanceChart({ data }: { data: EquipmentInsight[] }) {
  return (
    <div className="h-[380px] w-full">
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="equipment_type" />
          <YAxis yAxisId="percent" orientation="left" tickFormatter={(v) => `${Number(v).toFixed(2)}%`} />
          <YAxis yAxisId="count" orientation="right" />
          <Tooltip formatter={(value: number, name: string) => (name.includes("%") ? `${Number(value).toFixed(2)}%` : Number(value).toFixed(0))} />
          <Legend />
          <Bar yAxisId="percent" dataKey="booking_rate" name="Booking Rate %" fill="#0f6d92" radius={[6, 6, 0, 0]} />
          <Bar yAxisId="percent" dataKey="market_gap_pct" name="Final vs Market Gap %" fill="#1da9c3" radius={[6, 6, 0, 0]} />
          <Bar yAxisId="count" dataKey="calls" name="Calls" fill="#74d1e3" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
