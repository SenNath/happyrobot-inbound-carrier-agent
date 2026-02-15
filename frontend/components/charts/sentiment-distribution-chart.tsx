"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { SentimentDistributionPoint } from "@/lib/api";

export function SentimentDistributionChart({ data }: { data: SentimentDistributionPoint[] }) {
  const withColor = data.map((row) => ({
    ...row,
    fill:
      row.sentiment === "positive"
        ? "#15803d"
        : row.sentiment === "negative"
          ? "#b91c1c"
          : row.sentiment === "neutral"
            ? "#0f6d92"
            : "#64748b",
  }));
  return (
    <div className="h-[320px] w-full">
      <ResponsiveContainer>
        <BarChart data={withColor}>
          <CartesianGrid vertical={false} strokeDasharray="3 3" />
          <XAxis dataKey="sentiment" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Bar dataKey="count" radius={[8, 8, 0, 0]}>
            {withColor.map((entry) => (
              <Cell key={entry.sentiment} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
