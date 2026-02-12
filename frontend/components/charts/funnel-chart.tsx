"use client";

import { Cell, Funnel, FunnelChart, LabelList, ResponsiveContainer, Tooltip } from "recharts";

import type { FunnelStage } from "@/lib/api";

const colors = ["#0b3b5a", "#0f6d92", "#1da9c3"];

export function FunnelInsightsChart({ data }: { data: FunnelStage[] }) {
  return (
    <div className="h-[360px] w-full">
      <ResponsiveContainer>
        <FunnelChart>
          <Tooltip />
          <Funnel dataKey="value" data={data} isAnimationActive>
            <LabelList position="right" fill="#1f2f3c" stroke="none" dataKey="stage" />
            {data.map((entry, index) => (
              <Cell key={entry.stage} fill={colors[index % colors.length]} />
            ))}
          </Funnel>
        </FunnelChart>
      </ResponsiveContainer>
    </div>
  );
}
