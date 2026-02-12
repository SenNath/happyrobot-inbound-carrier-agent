"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { SentimentPoint } from "@/lib/api";

export function SentimentChart({ data }: { data: SentimentPoint[] }) {
  return (
    <div className="h-[360px] w-full">
      <ResponsiveContainer>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="sentimentFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#1da9c3" stopOpacity={0.45} />
              <stop offset="95%" stopColor="#1da9c3" stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="date" />
          <YAxis domain={[-1, 1]} />
          <Tooltip />
          <Area type="monotone" dataKey="avg_sentiment" stroke="#0f6d92" strokeWidth={3} fill="url(#sentimentFill)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
