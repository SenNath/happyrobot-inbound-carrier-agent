"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { NegotiationInsight } from "@/lib/api";

export function DecisionChart({ data }: { data: NegotiationInsight[] }) {
  return (
    <div className="h-[360px] w-full">
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
          <CartesianGrid vertical={false} strokeDasharray="3 3" />
          <XAxis dataKey="decision" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#0f6d92" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
