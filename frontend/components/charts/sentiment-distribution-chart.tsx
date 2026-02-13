"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { SentimentDistributionPoint } from "@/lib/api";

export function SentimentDistributionChart({ data }: { data: SentimentDistributionPoint[] }) {
  return (
    <div className="h-[320px] w-full">
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid vertical={false} strokeDasharray="3 3" />
          <XAxis dataKey="sentiment" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Bar dataKey="count" fill="#0f6d92" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
